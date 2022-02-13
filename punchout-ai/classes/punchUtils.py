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
        castedSpaces = spaces.Dict({
            'opponent_id': state.p2['character'],
            'opponent_action': state.p2['action'],
            'opponentTimer': state.p2['actionTimer'],
            'hearts': state.p1['hearts'],
            'stars': state.p1['stars'],
            'blinkingPink': state.p1['blinkingPink'],
            'bersekerAction': state.p1['bersekerAction']
        })

        # Each observation will be represented as a keras categorical value: a n
        # bits number with a single "1" that represents the category, where n is
        # the length of the dimension as specified in the spaces. We then flatten
        # the result array to get a single binary string that represents the full
        # state.

        result_array = []
        for item in castedSpaces.spaces.keys():
            classes = state_shape.spaces[item]
            result_array.append(to_categorical(np.unique(castedSpaces.spaces[item])[0], num_classes = np.unique(classes)[0].n, dtype ="int32"))
        flattened_spaces = [item for sublist in result_array for item in sublist]
        return flattened_spaces

    def calculateActionFromIndex(self, index):
        result ={}
        semiAction=self.actionMap[index]
        result[0]=int(semiAction[0])
        result[1]=int(semiAction[1])
        result[2]=int(semiAction[2])
        return result
