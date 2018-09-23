import gym
import punchout_ai
import os
import numpy as np
import threading
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from classes.bizhawkServer import BizHawkServer
from classes.runner import RunWrapper
from classes.Agent import Agent


class Program:
    def __init__(self):
        self.sample_batch_size = 32
        self.episodes = 10000
        self.env = gym.make("punchoutAI-v0")

        self.state_size = self.env.observation_space.n
        self.action_size = self.env.action_space.n
        self.agent = Agent(self.state_size, self.action_size)
        self.runner = None
        self.server = None

    def SetButtons(self, up, down, left, right, a, b):
        buttons = {'up': up,
                   'down': down,
                   'left': left,
                   'right': right,
                   'a': a,
                   'b': b}
        return buttons
    
    def sendCommandAndSpin(self, command:str):
        self.server.commandInQueue=command
        while(self.server.commandInQueue != None):
            pass

    def massageAction(self, action):
        tempCommands = self.SetButtons(False,False,False,False,False,False)

        if(action[0] == 1):
            tempCommands['up'] = True
        elif(action[0] == 2):
            tempCommands['right'] = True
        elif(action[0] == 3):
            tempCommands['down'] = True
        elif(action[0] == 4):
            tempCommands['left'] = True

        if(action[1] == 1):
            tempCommands['a'] = True
        elif(action[1] == 2):
            tempCommands['b'] = True

        return tempCommands

    def run(self):
        self.runner = RunWrapper()
        self.server = BizHawkServer(self.runner)
        self.server.start()
        try:
            for index_episode in range(self.episodes):
                self.server.buttons = self.SetButtons(
                    False, False, False, False, False, False)
                self.sendCommandAndSpin('reset')
                self.sendCommandAndSpin('GetState')
                self.env.setState(self.server.publicState)
                self.server.publicState=None
                state=self.env.reset()
                state = np.reshape(state, [1, self.state_size])

                done = False
                index = 0
                while not done:
                    action = self.agent.act(state)
                    self.server.buttons = self.massageAction(action)
                    self.sendCommandAndSpin('buttons')
                    next_state, reward, done, _ = self.env.step(action)
                    next_state = np.reshape(next_state, [1, self.state_size])
                    self.agent.remember(
                        state, action, reward, next_state, done)
                    state = next_state
                    index += 1
                print("Episode {}# Score: {}".format(index_episode, index + 1))
                self.agent.replay(self.sample_batch_size)
        finally:
            self.agent.save_model()


if __name__ == "__main__":
    program = Program()
    program.run()
