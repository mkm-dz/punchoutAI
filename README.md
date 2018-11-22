Punchout AI
-----------------
Nintendo's (TM) Mike Tyson Punchout played by an AI bot using Bizhawk emulator. 

Inspired and based on GyroscopeHQ's Street fighter bot.

Setup
---------
- Get python 3.6 (newer version may work as well)
- Clone the repository and pull the submodules (git submodule update --init for the Bizhawk submodule)
- Go to the BizHawkPunchOutAI folder and build the solution
- Open the Emuhawk.exe executable and load the game.
- Start a fight against a character and save the state at the begining of the fight.
- Go to the punchout-ai *folder/classes* and modify the *savegamepath* variable (bizhawkClient.py and bizhawkServer.py) to point to the saved state create in the previous step.
- Go to the punchout-ai *folder/classes* and modify the *self.weight_backup* variable to match your character.
- Open your python console Go to the punchout-ai and run *pip install -e .* (note the dot at the end)

Run
---------
- Open Emuhawk.exe and load the game (game need to be loaded before proceding)
- Go to the the *tools* menu and select *Punchout bot* entry
- An interface should pop, at this point everything seems frozen, this is ok as the port is waiting for instructions
- Run *runBot.py*
- You should see Bizhawk and the *runBot.py* script interacting.
