
import gym
import random
import os
import tensorflow as tf
import numpy as np
import tensorflow.keras as keras
import pathlib

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as K

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, BoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from rl.core import Processor
from rl.callbacks import Callback

from classes.AgentActionWrapper import AgentActionWrapper
from classes.punchUtils import punchUtils

class MyAgentCallback(Callback):
    def __init__(self,episode_begin_callback, episode_end_callback, verbose=False):
        self.episode_end_callback = episode_end_callback
        self.episode_begin_callback = episode_begin_callback
        self.verbose = verbose
        super(Callback, self)

    def on_episode_begin(self, episode, logs={}):
        self.rewardArray = []
        self.rewardIndex = -1
        self.command = AgentActionWrapper()

    def on_episode_end(self, episode, logs={}):
        """Called at end of each episode"""
        episode_reward = 0
        reward_index = 0
        for item in self.rewardArray:
            if(reward_index == len(self.rewardArray)-1):
                break

            episode_reward = episode_reward + item
            reward_index = reward_index + 1

        if(self.verbose):
            print(episode_reward)

        logPath = os.path.join(pathlib.Path().absolute() ,'ElMarrano.log')
        with open(logPath, 'a') as log_file:
            log_file.write(str(episode_reward)+'\n')

        pass

    def on_step_begin(self, step, logs={}):
        # Called at beginning of each step
        if(self.verbose):
            print("** Step Begin")
        self.command.envCommand = 'resume'
        self.command.agentAction = None
        self.rewardIndex = self.rewardIndex + 1

    def on_step_end(self, step, logs={}):
        # Called at end of each step
        if(logs['reward'] is not None):
            self.rewardArray.append(float(logs['reward']))
        if(self.verbose):
            print("** Step End")

    def on_action_begin(self, action, logs={}):
        pass
        #print("** Action Begin")

    def on_action_end(self, action, logs={}):
        pass
        #print("** Action End")

    def on_train_end(self, logs={}):
        self.episode_end_callback()

    def on_train_begin(self, logs={}):
        self.episode_begin_callback()

class MyProcessor(Processor):
    def __init__(self, verbose):
        self.punchUtils = punchUtils()
        self.wrapper = AgentActionWrapper()
        self.verbose = verbose
        super(Processor, self)

    def process_observation(self, observation):
        if(self.verbose):
            print ("I see:")
            print(self.punchUtils.castObservationArrayToObservation(observation))
        return observation

    def process_action(self, action_index):
        self.wrapper.agentAction = self.punchUtils.calculateActionFromIndex(action_index)
        self.wrapper.envCommand = 'sendButtons'
        if(self.verbose):
            print ("I do:")
            print(self.punchUtils.castAgentActionToEmuAction(self.wrapper.agentAction))
        return self.wrapper

    def process_state_batch(self, batch):
        return batch

class KerasAgentRunner():

    brain=None
    verbose = False
    def __init__(self, state_size, action_space):
        self.weight_backup = "ElMarrano"
        self.state_size = state_size
        self.action_space =  action_space
        self.action_space_size = 1
        for index in range(0, action_space.n):
            self.action_space_size *= action_space.spaces[index].n
        self.brain = self._build_model()

    def _build_model(self):
        logPath = os.path.join(pathlib.Path().absolute() , 'ElMarrano.log')
        with open(logPath, 'w+'):
            pass
        # Neural Net for Deep-Q learning Model
        model = Sequential()

        # Not really sure this is doing what I expect it is doing (batch_size, input_dim)
        model.add(Dense(self.state_size, input_shape=(1,) + (1, self.state_size), activation='relu'))
        model.add(Dense(self.state_size*2, activation='relu'))
        model.add(Dense(self.state_size*2, activation='relu'))
        model.add(Flatten())
        model.add(Dense(self.action_space_size, activation='linear'))

        memory = SequentialMemory(limit=500000, window_length=1)
        policy = BoltzmannQPolicy()
        self.dqn = DQNAgent(model=model, processor=MyProcessor(self.verbose),nb_actions=self.action_space_size, memory=memory, nb_steps_warmup=200,
        target_model_update=1e-2, policy=policy)
        self.dqn.compile(Adam(lr=1e-3), metrics=['mae'])
        return model

    def getRandomAction(self, observation):
        result={}
        spacesLength=len(self.action_space.spaces)
        for index in range(0, spacesLength):
            result[index]=random.randint(0, self.action_space.spaces[index].n-1)
        return result

    def save_model(self):
        self.dqn.save_weights(self.weight_backup+".dqn", True)

    def load_model(self):
        if os.path.isfile(self.weight_backup):
            self.dqn.load_weights(self.weight_backup+".dqn")

    def run(self, env):
        #start policy only gets called when there are warmup steps (nb_max steps)
        callback = [MyAgentCallback(self.load_model, self.save_model, self.verbose)]
        self.dqn.fit(env,nb_steps=10000,
        visualize=True,
        verbose=2,
        callbacks=callback,
        start_step_policy=self.getRandomAction)