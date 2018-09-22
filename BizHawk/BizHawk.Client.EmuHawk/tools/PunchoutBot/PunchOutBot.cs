using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Linq;
using System.Text;
using Newtonsoft.Json;


using System.Windows.Forms;


using BizHawk.Client.EmuHawk.ToolExtensions;

using BizHawk.Emulation.Common;
using BizHawk.Client.Common;

namespace BizHawk.Client.EmuHawk
{
	public partial class PunchOutBot : ToolFormBase , IToolFormAutoConfig
	{
		private const string DialogTitle = "PunchOut Bot";

		private string _currentFileName = "";

		private string CurrentFileName
		{
			get { return _currentFileName; }
			set
			{
				_currentFileName = value;

				if (!string.IsNullOrWhiteSpace(_currentFileName))
				{
					Text = DialogTitle + " - " + Path.GetFileNameWithoutExtension(_currentFileName);
				}
				else
				{
					Text = DialogTitle;
				}
			}

		}

		private bool _isBotting = false;


		private bool _replayMode = false;
		private string _lastRom = "";

		private bool _dontUpdateValues = false;

		private MemoryDomain _currentDomain;
		private bool _bigEndian;
		private int _dataSize;

		private int _wins = 0;
		private int _losses = 0;
		private int _p2_wins = 0;
		private int _p2_losses = 0;
		private string _lastResult = "Unknown";
		private float _winsToLosses = 0;
		private float _p2_winsToLosses = 0;
		private int _totalGames = 0;
		private int _OSDMessageTimeInSeconds = 15;
		private int _post_round_wait_time = 0;
		public bool game_in_progress = false;

		private ILogEntryGenerator _logGenerator;
		private TcpClient client;
		private TcpClient client_p2;

		#region Services and Settings

		[RequiredService]
		private IEmulator Emulator { get; set; }

		// Unused, due to the use of MainForm to loadstate, but this needs to be kept here in order to establish an IStatable dependency
		[RequiredService]
		private IStatable StatableCore { get; set; }

		[RequiredService]
		private IMemoryDomains MemoryDomains { get; set; }

		[ConfigPersist]
		public PunchOutBotSettings Settings { get; set; }

		public class PunchOutBotSettings
		{
			public PunchOutBotSettings()
			{
				RecentBotFiles = new RecentFiles();
				TurboWhenBotting = true;
			}

			public RecentFiles RecentBotFiles { get; set; }
			public bool TurboWhenBotting { get; set; }
		}

		#endregion

		#region sockethandling
		private TcpClient CreateTCPClient(string IP, int port)
		{
			return new TcpClient(IP, port);
		}
		
		private ControllerCommand SendEmulatorGameStateToController(TcpClient cl)
		{
			ControllerCommand cc = new ControllerCommand();
			try
			{

				
				NetworkStream stream = cl.GetStream();
				byte[] bytes = new byte[1024];
				// Encode the data string into a byte array. 
				GameState gs = GetCurrentState();
				string data = JsonConvert.SerializeObject(gs);

				byte[] msg = Encoding.ASCII.GetBytes(data);
				stream.Write(msg, 0, msg.Length);

				StringBuilder myCompleteMessage = new StringBuilder();
				if (stream.CanRead)
				{
					byte[] myReadBuffer = new byte[1024];
					int numberOfBytesRead = 0;
					// Incoming message may be larger than the buffer size.
					do
					{
						numberOfBytesRead = stream.Read(myReadBuffer, 0, myReadBuffer.Length);
						myCompleteMessage.AppendFormat("{0}", Encoding.ASCII.GetString(myReadBuffer, 0, numberOfBytesRead));
					}
					while (stream.DataAvailable);
				}
				cc = JsonConvert.DeserializeObject<ControllerCommand>(myCompleteMessage.ToString().ToLower());
			}
			catch (ArgumentNullException ane)
			{
				cc.type = "__err__" + ane.ToString();
			}
			catch (SocketException se)
			{
				cc.type = "__err__" + se.ToString();
			}
			catch (Exception e)
			{
				cc.type = "__err__" + e.ToString();
			}
			return cc;
		}
		
		#endregion

		#region Initialize

		public PunchOutBot()
		{
			InitializeComponent();
			Text = DialogTitle;
			Settings = new PunchOutBotSettings();		
		}

		private void PunchOutBot_Load(object sender, EventArgs e)
		{
			StartBot();
		}

		#endregion

		#region punchout

		public int GetOpponentId()
		{
			return _currentDomain.PeekByte(0x0001);
		}

		public int GetHealthP1()
		{
			return _currentDomain.PeekByte(0x0391);
		}

		public int GetHealthP2()
		{
			return _currentDomain.PeekByte(0x0398);
		}

		public int GetOpponentAction()
		{
			return _currentDomain.PeekByte(0x003A);
		}

		public bool GetOpponentIsMoving()
		{
			if (_currentDomain.PeekByte(0x0039) <= 1)
			{
				return true;
			}
			return false;
		}

		public bool IsRoundStarted()
		{
			if (_currentDomain.PeekByte(0x0004) == 255)
			{
				return true;
			}

			return false;
		}

		private bool IsRoundOver()
		{
			return GetHealthP1() <= 0|| GetHealthP2() <= 0 || _currentDomain.PeekByte(0x0004) != 255;
		}

		private string GetRoundResult()
		{
			if (this.IsRoundOver())
			{
				if (GetHealthP2() > 0)
				{
					return "P2";
				}
				else
				{
					return "P1";
				}
			}
			else
			{
				return "NOT_OVER";
			}
		}

		public Dictionary<string, bool> GetJoypadButtons(int? controller = null)
		{
			var buttons = new Dictionary<string, bool>();
			var adaptor = Global.AutofireStickyXORAdapter;
			foreach (var button in adaptor.Source.Definition.BoolButtons)
			{
				if (!controller.HasValue)
				{
					buttons[button] = adaptor.IsPressed(button);
				}
				else if (button.Length >= 3 && button.Substring(0, 2) == "P" + controller)
				{
					buttons[button.Substring(3)] = adaptor.IsPressed("P" + controller + " " + button.Substring(3));
				}
			}
			return buttons;
		}
		
		public void SetJoypadButtons(Dictionary<string,bool> buttons, int? controller = null)
		{
			try
			{
				foreach (var button in buttons.Keys)
				{
					var invert = false;
					bool? theValue;
					var theValueStr = buttons[button].ToString();

					if (!string.IsNullOrWhiteSpace(theValueStr))
					{
						if (theValueStr.ToLower() == "false")
						{
							theValue = false;
						}
						else if (theValueStr.ToLower() == "true")
						{
							theValue = true;
						}
						else
						{
							invert = true;
							theValue = null;
						}
					}
					else
					{
						theValue = null;
					}

					var toPress = button.ToString();
					if (controller.HasValue)
					{
						toPress = "P" + controller + " " + button;
					}

					if (!invert)
					{
						if (theValue.HasValue) // Force
						{
							Global.LuaAndAdaptor.SetButton(toPress, theValue.Value);
							Global.ActiveController.Overrides(Global.LuaAndAdaptor);
						}
						else // Unset
						{
							Global.LuaAndAdaptor.UnSet(toPress);
							Global.ActiveController.Overrides(Global.LuaAndAdaptor);
						}
					}
					else // Inverse
					{
						Global.LuaAndAdaptor.SetInverse(toPress);
						Global.ActiveController.Overrides(Global.LuaAndAdaptor);
					}
				}
			}
			catch
			{
				/*Eat it*/
	}
}
		private class PlayerState
		{
			public PlayerState()
			{
			}
			public int character { get; set; }
			public int health { get; set; }

			public Dictionary<string, bool> buttons { get; set; }
			public bool InMove { get; set; }
			public int action{ get; set; }


		}
		private class GameState
		{
			public GameState()
			{
			}
			public PlayerState p1 { get; set; }
			public PlayerState p2 { get; set; }
			public int frame { get; set; }
			public string result { get; set; }
			public bool round_started { get; set; }
			public bool round_over { get; set; }
		}

		private GameState GetCurrentState()
		{
			PlayerState p1 = new PlayerState();
			PlayerState p2 = new PlayerState();
			GameState gs = new GameState();
			p1.health = GetHealthP1();
			p1.action = 0;
			p1.buttons = GetJoypadButtons(1);
			p1.character = -1;
			p1.InMove = false;

			p2.health = GetHealthP2();
			p2.action = GetOpponentAction();
			p2.buttons = GetJoypadButtons(2);
			p2.character = GetOpponentId();
			p2.InMove = GetOpponentIsMoving();


			gs.p1 = p1;
			gs.p2 = p2;
			gs.result = GetRoundResult();
			gs.frame = Emulator.Frame;
			gs.round_started = IsRoundStarted();
			gs.round_over = IsRoundOver();

			return gs;
		}
		#endregion

		#region IToolForm Implementation

		public bool UpdateBefore { get { return true; } }

		public void NewUpdate(ToolFormUpdateType type) { }

		public void UpdateValues()
		{
			Update(fast: false);
		}

		public void FastUpdate()
		{
			Update(fast: true);
		}

		public void Restart()
		{
			if (_currentDomain == null ||
				MemoryDomains.Contains(_currentDomain))
			{
				_currentDomain = MemoryDomains.MainMemory;
				_bigEndian = _currentDomain.EndianType == MemoryDomain.Endian.Big;
				_dataSize = 1;
			}

			if (_isBotting)
			{
				StopBot();
			}


			if (_lastRom != GlobalWin.MainForm.CurrentlyOpenRom)
			{
				_lastRom = GlobalWin.MainForm.CurrentlyOpenRom;
				SetupControlsAndProperties();
			}
		}

		public bool AskSaveChanges()
		{
			return true;
		}

		#endregion

		#region Control Events

		#region FileMenu

		private void FileSubMenu_DropDownOpened(object sender, EventArgs e)
		{
		}


		private void ExitMenuItem_Click(object sender, EventArgs e)
		{
			Close();
		}

		#endregion

		#region Options Menu

		private void OptionsSubMenu_DropDownOpened(object sender, EventArgs e)
		{
			TurboWhileBottingMenuItem.Checked = Settings.TurboWhenBotting;
			BigEndianMenuItem.Checked = _bigEndian;
		}

		private void MemoryDomainsMenuItem_DropDownOpened(object sender, EventArgs e)
		{
			MemoryDomainsMenuItem.DropDownItems.Clear();
			MemoryDomainsMenuItem.DropDownItems.AddRange(
				MemoryDomains.MenuItems(SetMemoryDomain, _currentDomain.Name)
				.ToArray());
		}

		private void BigEndianMenuItem_Click(object sender, EventArgs e)
		{
			_bigEndian ^= true;
		}

		private void DataSizeMenuItem_DropDownOpened(object sender, EventArgs e)
		{
			_1ByteMenuItem.Checked = _dataSize == 1;
			_2ByteMenuItem.Checked = _dataSize == 2;
			_4ByteMenuItem.Checked = _dataSize == 4;
		}

		private void _1ByteMenuItem_Click(object sender, EventArgs e)
		{
			_dataSize = 1;
		}

		private void _2ByteMenuItem_Click(object sender, EventArgs e)
		{
			_dataSize = 2;
		}

		private void _4ByteMenuItem_Click(object sender, EventArgs e)
		{
			_dataSize = 4;
		}

		private void TurboWhileBottingMenuItem_Click(object sender, EventArgs e)
		{
			Settings.TurboWhenBotting ^= true;
		}

		#endregion

		private void RunBtn_Click(object sender, EventArgs e)
		{
			StartBot();
		}

		private void StopBtn_Click(object sender, EventArgs e)
		{
			StopBot();
		}





	
		private void ClearStatsContextMenuItem_Click(object sender, EventArgs e)
		{
		
		}

		#endregion

		#region Classes

		private class ControllerCommand
		{
			public ControllerCommand() { }
			public string type { get; set; }
			public Dictionary<string, bool> p1 { get; set; }
			public Dictionary<string, bool> p2 { get; set; }
			public string savegamepath { get; set; }

		}

		
		

		#endregion

		#region File Handling

		private void LoadFileFromRecent(string path)
		{
			var result = LoadBotFile(path);
			if (!result)
			{
				Settings.RecentBotFiles.HandleLoadError(path);
			}
		}

		private bool LoadBotFile(string path)
		{
	
			return true;
		}

		private void SaveBotFile(string path)
		{

		}

		#endregion

		private void SetupControlsAndProperties()
		{
			UpdateBotStatusIcon();
		}

		private void SetMemoryDomain(string name)
		{
			_currentDomain = MemoryDomains[name];
			_bigEndian = MemoryDomains[name].EndianType == MemoryDomain.Endian.Big;
		}

		private int GetRamvalue(int addr)
		{
			int val;
			switch (_dataSize)
			{
				default:
				case 1:
					val = _currentDomain.PeekByte(addr);
					break;
				case 2:
					val = _currentDomain.PeekUshort(addr, _bigEndian);
					break;
				case 4:
					val = (int)_currentDomain.PeekUint(addr, _bigEndian);
					break;
			}

			return val;
		}

		private void Update(bool fast)
		{
			if (_dontUpdateValues)
			{
				return;
			}

			if (_isBotting)
			{

				if (IsRoundOver() && game_in_progress)
				{
					_post_round_wait_time--;
					game_in_progress = false;
					_totalGames = _totalGames + 1;
					if (GetRoundResult() == "P1")
					{
						_wins = _wins + 1;
						_lastResult = "P1 Win";
						_p2_losses = _p2_losses + 1;

					}
					else
					{
						_losses = _losses + 1;
						_lastResult = "P1 Loss";
						_p2_wins = _p2_wins + 1;
					}

					_winsToLosses = (float)_wins / _totalGames;
					_p2_winsToLosses = (float)_p2_wins / _totalGames;
					GlobalWin.OSD.ClearGUIText();
					GlobalWin.OSD.AddMessageForTime("Game #: " + _totalGames + " | Last Result: " + _lastResult + " | P1 Wins-Losses: " + _wins + "-" + _losses + " (" + _winsToLosses + ") | P2 Wins-Losses: " + _p2_wins + "-" + _p2_losses + " (" + _p2_winsToLosses + ")", _OSDMessageTimeInSeconds);
				}
				if (_post_round_wait_time < Global.Config.round_over_delay)
				{
					if (_post_round_wait_time < 1)
					{
						_post_round_wait_time = Global.Config.round_over_delay;
						if (Global.Config.pause_after_round)
						{
							GlobalWin.MainForm.PauseEmulator();
							return;
						}
					}
					else
					{
						_post_round_wait_time--;
						return;
					}
				}


				string command_type = "";
				do
				{
					// send over the current game state
					ControllerCommand command = SendEmulatorGameStateToController(this.client);
					ControllerCommand command_p2;

					command_type = command.type;

					if (Global.Config.use_two_controllers)
					{
						do
						{
							command_p2 = SendEmulatorGameStateToController(this.client_p2);
							//Console.WriteLine("p1 command: "  + command.type + "p2 command: "  + command_p2.type);
							// send the game state to the controller
							// if the commands don't match, wait until they do.
						} while (command_p2.type != command_type);
						// if we get a buttons command, replace the buttons of first emulator's set for it's p2 (which
						// is null) with the buttons we want to actually play from this emulator's set of buttons. 
						// we do this so we only need one command object after this code block.
						if (command_type == "buttons")
						{
							command.p2 = command_p2.p2;
						}
					
					}


					// get a command back
					// act on the command
					if (command_type == "reset")
					{
						GlobalWin.MainForm.LoadState(command.savegamepath, Path.GetFileName(command.savegamepath));
						game_in_progress = true;
					}
					else if (command_type == "processing")
					{
						// just do nothing, we're waiting for feedback from the controller.
						// XXX how do we tell the emulator to not advance the frame?

					}
					else
					{
						SetJoypadButtons(command.p1, 1);
						if (Global.Config.use_two_controllers)
						{
							SetJoypadButtons(command.p2, 2);
							
						}
					}
				} while (command_type == "processing");





				// press the buttons if need be
				//PressButtons();
			}
		}


		private void StartBot()
		{
			if (!CanStart())
			{
				MessageBox.Show("Unable to run with current settings");
				return;
			}

			_isBotting = true;
			RunBtn.Visible = false;
			StopBtn.Visible = true;
			this.client = CreateTCPClient(Global.Config.controller_ip, Global.Config.controller_port);
			if (Global.Config.use_two_controllers)
			{
				this.client_p2 = CreateTCPClient(Global.Config.controller_ip_p2, Global.Config.controller_port_p2);
			}

			Global.Config.SoundEnabled = false;
			GlobalWin.MainForm.UnpauseEmulator();
			SetMaxSpeed();
			if (Global.Config.emulator_speed_percent != 6399) {
				SetNormalSpeed();
			}
			GlobalWin.MainForm.ClickSpeedItem(Global.Config.emulator_speed_percent);
			//if (Settings.TurboWhenBotting)
			//{
			//	SetMaxSpeed();
			//}

			UpdateBotStatusIcon();
			MessageLabel.Text = "Running...";
			_logGenerator = Global.MovieSession.LogGeneratorInstance();
			_logGenerator.SetSource(Global.ClickyVirtualPadController);
			_post_round_wait_time = Global.Config.round_over_delay;
			GlobalWin.OSD.AddMessageForTime("Game #: 0 Last Result: N/A P1 Wins-Losses: " + _wins + "-" + _losses + " (" + _winsToLosses + ") P2 Wins-Losses: " + _p2_wins + "-" + _p2_losses + "(" + _p2_winsToLosses + ")", _OSDMessageTimeInSeconds);

		}

		private bool CanStart()
		{
		

			return true;
		}

		private void StopBot()
		{
			RunBtn.Visible = true;
			StopBtn.Visible = false;
			_isBotting = false;
	
			

			GlobalWin.MainForm.PauseEmulator();
			SetNormalSpeed();
			UpdateBotStatusIcon();
			MessageLabel.Text = "Bot stopped";
		}

		private void UpdateBotStatusIcon()
		{
			if (_replayMode)
			{
				BotStatusButton.Image = Properties.Resources.Play;
				BotStatusButton.ToolTipText = "Replaying best result";
			}
			else if (_isBotting)
			{
				BotStatusButton.Image = Properties.Resources.RecordHS;
				BotStatusButton.ToolTipText = "Botting in progress";
			}
			else
			{
				BotStatusButton.Image = Properties.Resources.Pause;
				BotStatusButton.ToolTipText = "Bot is currently not running";
			}
		}

		private void SetMaxSpeed()
		{
			GlobalWin.MainForm.Unthrottle();
		}

		private void SetNormalSpeed()
		{
			GlobalWin.MainForm.Throttle();
		}


		

	}
}
