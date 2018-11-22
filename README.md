Punchout AI
-----------------
Nintendo's (TM) Mike Tyson Punchout played by an AI bot using Bizhawk emulator. 

Inspired and based on GyroscopeHQ's Street fighter bot.

How to run
---------
- Clone the repository and pull the submodules
- Go to the BizHawkPunchOutAI folder and build the solution
- Open the Emuhawk.exe executable and load the game.
- Start a fight against a character and save the state at the beggining of the fight.
- Go to the punchout-ai *folder/classes* and modify the *savegamepath* variable (bizhawkClient.py and bizhawkServer.py) to point to the saved state create in the previous step.
- Go to the punchout-ai *folder/classes* and modify the *self.wight_backup* variable to match your character.
- Run the runBot.py script.

