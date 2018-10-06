import gym
import punchout_ai
import os
import numpy as np
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from classes.bizhawkServer import BizHawkServer
from classes.bizhawkClient import BizHawkClient
from classes.Agent import Agent


class Program:
    def __init__(self):
        self.sample_batch_size = 32
        self.episodes =90
        self.env = gym.make("punchoutAI-v0")

        self.state_size = self.env.observation_space.n
        self.action_size = self.env.action_space.n
        self.agent = Agent(self.state_size, self.env.action_space)
        self.server = BizHawkServer()

    def SetButtons(self, up, down, left, right, a, b):
        buttons = {'Up': up,
                   'Down': down,
                   'Left': left,
                   'Right': right,
                   'A': a,
                   'B': b}
        return buttons
    
    def sendCommand(self, command:str, buttons=None):
        client = BizHawkClient()
        if(buttons == None):
            client.buttons = self.SetButtons(
                    False, False, False, False, False, False)
        else:
            client.buttons = buttons
        client.Send(command)

    def WaitForServer(self) -> str:
        while(self.server.publicState == None):
            pass
        tempState = self.server.publicState
        self.server.publicState = None
        return tempState

    def massageAction(self, action):
        tempCommands = self.SetButtons(False,False,False,False,False,False)

        if(action[0] == 1):
            tempCommands['A'] = True
        elif(action[0] == 2):
            tempCommands['B'] = True

        if(action[1] == 1):
            tempCommands['Up'] = True
        elif(action[1] == 2):
            tempCommands['Right'] = True
        elif(action[1] == 3):
            tempCommands['Down'] = True
        elif(action[1] == 4):
            tempCommands['Left'] = True

        return tempCommands

    def run(self):
        self.server.start()
        while(self.server.ready == False):
            pass
        try:
            for index_episode in range(self.episodes):
                self.sendCommand('reset')
                self.WaitForServer()
                self.sendCommand('get_state')
                currentState = self.WaitForServer()
                self.env.setState(currentState)
                state=self.env.reset()
                state = np.reshape(state, [1, self.state_size])

                done = False
                totalReward = 0
                while not done:
                #while True:
                    action = self.agent.act(state)
                    actionButtons = self.massageAction(action)
                    self.sendCommand('buttons', actionButtons)
                    currentState=self.WaitForServer()
                    self.env.setState(currentState)
                    next_state, reward, done, _ = self.env.step(action)
                    next_state = np.reshape(next_state, [1, self.state_size])
                    self.agent.remember(
                        state, action, reward, next_state, done)
                    state = next_state
                    totalReward += reward
                print("Episode {}# Score: {}".format(index_episode, totalReward))
                self.agent.replay(self.sample_batch_size)
        finally:
            #self.agent.save_model()
            pass


if __name__ == "__main__":
    program = Program()
    program.run()
