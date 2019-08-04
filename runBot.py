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
        self.episodes =500
        self.full_range =3
        self.env = gym.make("punchoutAI-v0")

        self.state_size = self.env.observation_space.n
        self.agent = Agent(self.state_size, self.env.action_space)

    def run(self):
        for full_cycle in range(self.full_range):
            print("*********** SEPARATION *************")
            try:
                for index_episode in range(self.episodes):
                    self.env.reset()
                    done = False
                    totalReward = 0
                    counter = 0
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

                        self.agent.remember(
                            state, next_state, reward)
                        totalReward += reward
                        counter+=1
                    print("Episode:|{}|Total Reward:|{}".format(index_episode, (totalReward/counter)))
            finally:
                self.agent.save_model()
                print(self.agent.brain.summary())
                pass


if __name__ == "__main__":
    program = Program()
    program.run()
