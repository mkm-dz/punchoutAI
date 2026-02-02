from classes.bizhawkClient import BizHawkClient
from gym import error, spaces
import numpy as np
from tensorflow.keras.utils import to_categorical 

class punchUtils():
    def __init__(self):
        # We have an output space of 72 possible actions (moves)

        # we map each one to a controller action
        # First digit = timing 0-Low 1-Medium 2-High
        # second digit = buttons 0-None 1-A 2-B 3-Start
        # third digit = direction 0-None 1-Up 2-Right 3-Down 4-Left 5-DoubleTapDown
        self.actionMap={}
        # Timing 0 (Low) - 24 actions (0-23)
        self.actionMap[0] =  '000'  # No button, no direction (idle)
        self.actionMap[1] =  '001'  # No button, Up
        self.actionMap[2] =  '002'  # No button, Right (dodge right)
        self.actionMap[3] =  '003'  # No button, Down
        self.actionMap[4] =  '004'  # No button, Left (dodge left)
        self.actionMap[5] =  '005'  # No button, DoubleTapDown (duck)
        self.actionMap[6] =  '010'  # A button (left jab), no direction
        self.actionMap[7] =  '011'  # A button (left jab), Up (face punch)
        self.actionMap[8] =  '012'  # A button (left jab), Right
        self.actionMap[9] =  '013'  # A button (left jab), Down (body blow)
        self.actionMap[10] = '014'  # A button (left jab), Left
        self.actionMap[11] = '015'  # A button (left jab), DoubleTapDown (duck)
        self.actionMap[12] = '020'  # B button (right jab), no direction
        self.actionMap[13] = '021'  # B button (right jab), Up (face punch)
        self.actionMap[14] = '022'  # B button (right jab), Right
        self.actionMap[15] = '023'  # B button (right jab), Down (body blow)
        self.actionMap[16] = '024'  # B button (right jab), Left
        self.actionMap[17] = '025'  # B button (right jab), DoubleTapDown (duck)
        self.actionMap[18] = '030'  # Start button (star uppercut), no direction
        self.actionMap[19] = '031'  # Start button (star uppercut), Up
        self.actionMap[20] = '032'  # Start button (star uppercut), Right
        self.actionMap[21] = '033'  # Start button (star uppercut), Down
        self.actionMap[22] = '034'  # Start button (star uppercut), Left
        self.actionMap[23] = '035'  # Start button (star uppercut), DoubleTapDown (duck)
        # Timing 1 (Medium) - 24 actions (24-47)
        self.actionMap[24] = '100'  # No button, no direction
        self.actionMap[25] = '101'  # No button, Up
        self.actionMap[26] = '102'  # No button, Right
        self.actionMap[27] = '103'  # No button, Down
        self.actionMap[28] = '104'  # No button, Left
        self.actionMap[29] = '105'  # No button, DoubleTapDown (duck)
        self.actionMap[30] = '110'  # A button (left jab), no direction
        self.actionMap[31] = '111'  # A button (left jab), Up (face punch)
        self.actionMap[32] = '112'  # A button (left jab), Right
        self.actionMap[33] = '113'  # A button (left jab), Down (body blow)
        self.actionMap[34] = '114'  # A button (left jab), Left
        self.actionMap[35] = '115'  # A button (left jab), DoubleTapDown (duck)
        self.actionMap[36] = '120'  # B button (right jab), no direction
        self.actionMap[37] = '121'  # B button (right jab), Up (face punch)
        self.actionMap[38] = '122'  # B button (right jab), Right
        self.actionMap[39] = '123'  # B button (right jab), Down (body blow)
        self.actionMap[40] = '124'  # B button (right jab), Left
        self.actionMap[41] = '125'  # B button (right jab), DoubleTapDown (duck)
        self.actionMap[42] = '130'  # Start button (star uppercut), no direction
        self.actionMap[43] = '131'  # Start button (star uppercut), Up
        self.actionMap[44] = '132'  # Start button (star uppercut), Right
        self.actionMap[45] = '133'  # Start button (star uppercut), Down
        self.actionMap[46] = '134'  # Start button (star uppercut), Left
        self.actionMap[47] = '135'  # Start button (star uppercut), DoubleTapDown (duck)
        # Timing 2 (High) - 24 actions (48-71)
        self.actionMap[48] = '200'  # No button, no direction
        self.actionMap[49] = '201'  # No button, Up
        self.actionMap[50] = '202'  # No button, Right
        self.actionMap[51] = '203'  # No button, Down
        self.actionMap[52] = '204'  # No button, Left
        self.actionMap[53] = '205'  # No button, DoubleTapDown (duck)
        self.actionMap[54] = '210'  # A button (left jab), no direction
        self.actionMap[55] = '211'  # A button (left jab), Up (face punch)
        self.actionMap[56] = '212'  # A button (left jab), Right
        self.actionMap[57] = '213'  # A button (left jab), Down (body blow)
        self.actionMap[58] = '214'  # A button (left jab), Left
        self.actionMap[59] = '215'  # A button (left jab), DoubleTapDown (duck)
        self.actionMap[60] = '220'  # B button (right jab), no direction
        self.actionMap[61] = '221'  # B button (right jab), Up (face punch)
        self.actionMap[62] = '222'  # B button (right jab), Right
        self.actionMap[63] = '223'  # B button (right jab), Down (body blow)
        self.actionMap[64] = '224'  # B button (right jab), Left
        self.actionMap[65] = '225'  # B button (right jab), DoubleTapDown (duck)
        self.actionMap[66] = '230'  # Start button (star uppercut), no direction
        self.actionMap[67] = '231'  # Start button (star uppercut), Up
        self.actionMap[68] = '232'  # Start button (star uppercut), Right
        self.actionMap[69] = '233'  # Start button (star uppercut), Down
        self.actionMap[70] = '234'  # Start button (star uppercut), Left
        self.actionMap[71] = '235'  # Start button (star uppercut), DoubleTapDown (duck)

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
        elif(agentAction[2] == 5):
            # Double-tap down for duck/crouch - treated as its own button
            tempCommands['DoubleTapDown'] = True

        return tempCommands

    def castEmuStateToObservation(self, state, state_shape):
        # Changed from one-hot encoding to normalized float values
        # This is much more efficient: 12 floats instead of 870 bits
        # Neural networks can learn better from continuous normalized values
        # Removed elapsed time (minutes/seconds/decimals) - time creates noise in learning
        
        observation = np.array([
            state.p2['character'] / 20.0,        # Opponent ID (0-1)
            state.p2['action'] / 256.0,          # Opponent state (0-1)
            state.p1['hearts'] / 60.0,           # Player hearts (0-1)
            state.p1['stars'] / 20.0,            # Player stars (0-1)
            float(state.p1['blinkingPink']),     # Blinking pink (0 or 1)
            state.p1['bersekerAction'] / 256.0,  # Berserker action (0-1)
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
