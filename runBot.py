import gym
import punchout_ai
import os
import numpy as np
import time
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from classes.Agent import Agent
from classes.KerasRlAgent import KerasAgentRunner

class Program:
    def __init__(self):
        self.episodes =500
        self.full_range =3
        self.env = gym.make("punchoutAI-v0")

        self.state_size = self.env.observation_space.n
        self.agent_runner = KerasAgentRunner(self.state_size, self.env.action_space)

    def run(self):
        for full_cycle in range(self.full_range):
            print("*********** SEPARATION *************")
            self.agent_runner.run(self.env)

if __name__ == "__main__":
    program = Program()
    program.run()
