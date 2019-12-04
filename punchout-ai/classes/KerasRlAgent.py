
import gym
import random
import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam
from keras import backend as K

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, BoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from rl.core import Processor
from rl.callbacks import Callback

from classes.AgentActionWrapper import AgentActionWrapper
from classes.punchUtils import punchUtils

class MyAgentCallback(Callback):
    def __init__(self, episode_end_callback):
        self.episode_end_callback = episode_end_callback
        super(Callback, self)

    def on_episode_begin(self, episode, logs={}):
        self.command = AgentActionWrapper()

    def on_episode_end(self, episode, logs={}):
        """Called at end of each episode"""
        pass

    def on_step_begin(self, step, logs={}):
        # Called at beginning of each step
        print("** Step Begin")
        self.command.envCommand = 'resume'
        self.command.agentAction = None

    def on_step_end(self, step, logs={}):
        # Called at end of each step
        print("** Step End")

    def on_action_begin(self, action, logs={}):
        pass
        #print("** Action Begin")

    def on_action_end(self, action, logs={}):
        pass
        #print("** Action End")

    def on_train_end(self, logs={}):
        self.episode_end_callback()


class MyProcessor(Processor):
    def __init__(self):
        self.punchUtils = punchUtils()
        self.wrapper = AgentActionWrapper()
        super(Processor, self)

    def process_observation(self, observation):
        print ("I see:")
        print(self.punchUtils.castObservationArrayToObservation(observation))
        return observation

    def process_action(self, action_index):
        self.wrapper.agentAction = self.punchUtils.calculateActionFromIndex(action_index)
        self.wrapper.envCommand = 'sendButtons'
        print ("I do:")
        print(self.punchUtils.castAgentActionToEmuAction(self.wrapper.agentAction))
        return self.wrapper

    def process_state_batch(self, batch):
        return batch

class KerasAgentRunner():

    brain=None
    def __init__(self, state_size, action_space):
        self.weight_backup = "VonKaizer"
        self.state_size = state_size
        self.action_space =  action_space
        self.action_space_size = 1
        for index in range(0, action_space.n):
            self.action_space_size *= action_space.spaces[index].n
        self.brain = self._build_model()

    def _build_model(self):
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
        self.dqn = DQNAgent(model=model, processor=MyProcessor(),nb_actions=self.action_space_size, memory=memory, nb_steps_warmup=10,
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
        self.brain.save(self.weight_backup+".h5py")
        self.dqn.save_weights(self.weight_backup+".dqn", True)

    def run(self, env):
        #start policy only gets called when there are warmup steps (nb_max steps)
        callback = [MyAgentCallback(self.save_model)]
        self.dqn.fit(env,nb_steps=5000,
        visualize=True,
        verbose=2,
        callbacks=callback,
        start_step_policy=self.getRandomAction)