import gym
import punchout_ai
import os
import numpy as np
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from classes.Agent import Agent
from classes.AgentActionWrapper import AgentActionWrapper

class Program:
    def __init__(self):
        self.sample_batch_size = 128
        self.episodes =160
        self.env = gym.make("punchoutAI-v0")

        self.state_size = self.env.observation_space.n
        self.agent = Agent(self.state_size, self.env.action_space)

    def run(self):
        try:
            for index_episode in range(self.episodes):
                self.env.reset()
                done = False
                totalReward = 0
                command = {}
                command = AgentActionWrapper()
                while not done:
                    # Wait for oponent action
                    command.agentAction = None
                    command.envCommand = 'resume'
                    state, reward, done, _ = self.env.step(command)

                    # As the agent what to do next
                    action = self.agent.act(state)

                    # Send the action proposed by the agent, execute it and wait for the new state
                    command.agentAction = action
                    command.envCommand = 'sendButtons'
                    next_state, reward, done, _ = self.env.step(command)

                    # At this point next_state has the value at the action, meaning, if I connected a hit it has that value, be careful not to confuse this state with the "next available state" which is when the character is free to do it's next action.
                    #next_state = np.reshape(next_state, [1, self.state_size])
                    self.agent.remember(
                        state, next_state, reward)
                    totalReward += reward
                print("Episode {}# Score: {}".format(index_episode, totalReward))
                #self.agent.replay(self.sample_batch_size)
        finally:
            self.agent.save_model()
            print(self.agent.brain.summary())
            pass


if __name__ == "__main__":
    program = Program()
    program.run()
