from classes.bizhawkClient import BizHawkClient
from gym import error, spaces
import numpy as np
from tensorflow.keras.utils import to_categorical 

class punchUtils():
    def __init__(self):
        # We have an output space of 60 possible actions (moves)

        # we map each one to a controller action
        # First digit = timin 0-Low 1-Medium 2-High
        # second digit = buttons 0-None 1-A 2-B 3-Start
        # third digit = direction 0-None 1-Up 2-Right 3-Down 4-Left
        self.actionMap={}
        self.actionMap[0] =  '000'
        self.actionMap[1] =  '001'
        self.actionMap[2] =  '002'
        self.actionMap[3] =  '003'
        self.actionMap[4] =  '004'
        self.actionMap[5] =  '010'
        self.actionMap[6] =  '011'
        self.actionMap[7] =  '012'
        self.actionMap[8] =  '013'
        self.actionMap[9] =  '014'
        self.actionMap[10] = '020'
        self.actionMap[11] = '021'
        self.actionMap[12] = '022'
        self.actionMap[13] = '023'
        self.actionMap[14] = '024'
        self.actionMap[15] = '030'
        self.actionMap[16] = '031'
        self.actionMap[17] = '032'
        self.actionMap[18] = '033'
        self.actionMap[19] = '034'
        self.actionMap[20] = '100'
        self.actionMap[21] = '101'
        self.actionMap[22] = '102'
        self.actionMap[23] = '103'
        self.actionMap[24] = '104'
        self.actionMap[25] = '110'
        self.actionMap[26] = '111'
        self.actionMap[27] = '112'
        self.actionMap[28] = '113'
        self.actionMap[29] = '114'
        self.actionMap[30] = '120'
        self.actionMap[31] = '121'
        self.actionMap[32] = '122'
        self.actionMap[33] = '123'
        self.actionMap[34] = '124'
        self.actionMap[35] = '130'
        self.actionMap[36] = '131'
        self.actionMap[37] = '132'
        self.actionMap[38] = '133'
        self.actionMap[39] = '134'
        self.actionMap[40] = '200'
        self.actionMap[41] = '201'
        self.actionMap[42] = '202'
        self.actionMap[43] = '203'
        self.actionMap[44] = '204'
        self.actionMap[45] = '210'
        self.actionMap[46] = '211'
        self.actionMap[47] = '212'
        self.actionMap[48] = '213'
        self.actionMap[49] = '214'
        self.actionMap[50] = '220'
        self.actionMap[51] = '221'
        self.actionMap[52] = '222'
        self.actionMap[53] = '223'
        self.actionMap[54] = '224'
        self.actionMap[55] = '230'
        self.actionMap[56] = '231'
        self.actionMap[57] = '232'
        self.actionMap[58] = '233'
        self.actionMap[59] = '234'

    def sendCommand(self, command: str, buttons=None):
        client = BizHawkClient()
        if(buttons == None):
            client.buttons = self.SetButtons(
                False, False, False, False, False, False, False,'Low')
        else:
            client.buttons = buttons
        client.Send(command)

    def SetButtons(self, up, down, left, right, a, b, start, timing):
        buttons = {'Up': up,
                    'Down': down,
                    'Left': left,
                    'Right': right,
                    'A': a,
                    'B': b,
                    'Start': start,
                    'Timing': timing}
        return buttons

    def castAgentActionToEmuAction(self, agentAction):
        tempCommands = self.SetButtons(False,False,False,False,False,False,False,'Low')

        if(agentAction[0] == 1):
            tempCommands['Timing'] = 'Medium'
        elif(agentAction[0] == 2):
            tempCommands['Timing'] = 'High'

        if(agentAction[1] == 1):
            tempCommands['A'] = True
        elif(agentAction[1] == 2):
            tempCommands['B'] = True
        elif(agentAction[1] == 3):
            tempCommands['Start'] = True

        if(agentAction[2] == 1):
            tempCommands['Up'] = True
        elif(agentAction[2] == 2):
            tempCommands['Right'] = True
        elif(agentAction[2] == 3):
            tempCommands['Down'] = True
        elif(agentAction[2] == 4):
            tempCommands['Left'] = True

        return tempCommands

    def castEmuStateToObservation(self, state, state_shape):
        # Changed from one-hot encoding to normalized float values
        # This is much more efficient: 15 floats instead of 870 bits
        # Neural networks can learn better from continuous normalized values
        
        observation = np.array([
            state.p2['character'] / 20.0,        # Opponent ID (0-1)
            state.p2['action'] / 256.0,          # Opponent state (0-1)
            state.p1['hearts'] / 60.0,           # Player hearts (0-1)
            state.p1['stars'] / 20.0,            # Player stars (0-1)
            float(state.p1['blinkingPink']),     # Blinking pink (0 or 1)
            state.p1['bersekerAction'] / 256.0,  # Berserker action (0-1)
            state.elapsed_minutes / 10.0,        # Elapsed minutes (0-1, assuming max 10 min)
            state.elapsed_seconds / 60.0,        # Elapsed seconds (0-1)
            state.elapsed_decimals / 100.0,      # Elapsed decimals (0-1)
            state.opp_y_position / 256.0,        # Opponent Y position (0-1)
            state.opp_sprite_pos1 / 256.0,       # Opponent sprite pos 1 (0-1)
            state.opp_sprite_pos2 / 256.0,       # Opponent sprite pos 2 (0-1)
            state.opp_next_action_timer / 256.0, # Opponent next action timer (0-1)
            state.opp_next_action / 256.0,       # Opponent next action (0-1)
            state.opp_action_set / 256.0         # Opponent action set (0-1)
        ], dtype=np.float32)
        
        return observation

    def calculateActionFromIndex(self, index):
        result ={}
        semiAction=self.actionMap[index]
        result[0]=int(semiAction[0])
        result[1]=int(semiAction[1])
        result[2]=int(semiAction[2])
        return result
