from classes.bizhawkClient import BizHawkClient
from gym import error, spaces
import numpy as np

class punchUtils():

    def sendCommand(self, command: str, buttons=None):
        client = BizHawkClient()
        if(buttons == None):
            client.buttons = self.SetButtons(
                False, False, False, False, False, False)
        else:
            client.buttons = buttons
        client.Send(command)

    def SetButtons(self, up, down, left, right, a, b):
        buttons = {'Up': up,
                    'Down': down,
                    'Left': left,
                    'Right': right,
                    'A': a,
                    'B': b}
        return buttons

    def castAgentActionToEmuAction(self, agentAction):
        tempCommands = self.SetButtons(False,False,False,False,False,False)

        if(agentAction[0] == 1):
            tempCommands['A'] = True
        elif(agentAction[0] == 2):
            tempCommands['B'] = True

        if(agentAction[1] == 1):
            tempCommands['Up'] = True
        elif(agentAction[1] == 2):
            tempCommands['Right'] = True
        elif(agentAction[1] == 3):
            tempCommands['Down'] = True
        elif(agentAction[1] == 4):
            tempCommands['Left'] = True

        return tempCommands

    def castEmuStateToObservation(self, state):
        castedSpaces = spaces.Dict({
            'opponent_id': state.p2['character'],
            'opponent_action': state.p2['action'],
            'opponentTimer': state.p2['actionTimer'],
            'secondary_opponent_action': state.p2['secondaryAction'],
            'hearts': state.p1['hearts'],
            'result': state.result,
            'canThrowPunches': state.p1['canThrowPunches']
        })
        return np.fromiter(castedSpaces.spaces.values(), dtype=int)