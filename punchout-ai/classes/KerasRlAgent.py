
import gym
import random
import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras import backend as K

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, BoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from rl.core import Processor
from rl.callbacks import Callback

from classes.AgentActionWrapper import AgentActionWrapper

class MyAgentCallback(Callback):
    def on_episode_begin(self, episode, logs={}):
        self.currentStep = 0
        self.totalReward = 0
        self.command = AgentActionWrapper()

    def on_step_begin(self, step, logs={}):
        # Called at beginning of each step
        self.command = self.processStep()

    def on_step_end(self, step, logs={}):
        if(self.currentStep < 1):
            self.currentStep += 1
        else:
            self.currentStep = 0

    def on_action_begin(self, action, logs={}):
        """Called at beginning of each action"""
        pass

    def on_action_end(self, action, logs={}):
        """Called at end of each action"""
        pass
    def processStep(self):
       currentCommand = self.command
       if(self.currentStep == 0):
            currentCommand.agentAction = None
            currentCommand.envCommand = 'resume'
       elif (self.currentStep == 1):
            currentCommand.agentAction = action
            currentCommand.envCommand = 'sendButtons'
       return currentCommand


class MyProcessor(Processor):
    def process_observation(self, observation):
        return observation
    def process_action(self, action):
        return action

class KerasAgentRunner():

    brain=None
    def __init__(self, state_size, action_space):
        self.weight_backup = "VonKaizer.h5py"
        self.state_size = state_size
        self.action_space =  action_space
        self.action_space_size = 1
        for index in range(0, action_space.n):
            self.action_space_size *= action_space.spaces[index].n
        self.learning_rate = 0.05
        self.gamma = 0.95
        self.exploration_rate = 1.0
        self.exploration_min = 0.15
        self.exploration_decay = 0.9999
        self.brain = self._build_model()

    def createMapping(self):
        # We have an output space of 60 possible actions (moves)

        # we map each one to a controller action
        # First digit = timin 0-Low 1-Medium 2-High
        # second digit = buttons 0-None 1-A 2-B 3-Start
        # third digit = direction 0-None 1-Up 2-Right 3-Down 4-Left
        result={}
        result[0] =  '000'
        result[1] =  '001'
        result[2] =  '002'
        result[3] =  '003'
        result[4] =  '004'
        result[5] =  '010'
        result[6] =  '011'
        result[7] =  '012'
        result[8] =  '013'
        result[9] =  '014'
        result[10] = '020'
        result[11] = '021'
        result[12] = '022'
        result[13] = '023'
        result[14] = '024'
        result[15] = '030'
        result[16] = '031'
        result[17] = '032'
        result[18] = '033'
        result[19] = '034'
        result[20] = '100'
        result[21] = '101'
        result[22] = '102'
        result[23] = '103'
        result[24] = '104'
        result[25] = '110'
        result[26] = '111'
        result[27] = '112'
        result[28] = '113'
        result[29] = '114'
        result[30] = '120'
        result[31] = '121'
        result[32] = '122'
        result[33] = '123'
        result[34] = '124'
        result[35] = '130'
        result[36] = '131'
        result[37] = '132'
        result[38] = '133'
        result[39] = '134'
        result[40] = '200'
        result[41] = '201'
        result[42] = '202'
        result[43] = '203'
        result[44] = '204'
        result[45] = '210'
        result[46] = '211'
        result[47] = '212'
        result[48] = '213'
        result[49] = '214'
        result[50] = '220'
        result[51] = '221'
        result[52] = '222'
        result[53] = '223'
        result[54] = '224'
        result[55] = '230'
        result[56] = '231'
        result[57] = '232'
        result[58] = '233'
        result[59] = '234'

        return result

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(self.state_size, input_dim=self.state_size, 
        activation='relu'))
        model.add(Dense((self.state_size+(self.action_space_size* 2)), activation='relu'))
        model.add(Dense(self.action_space_size*2, activation='relu'))
        model.add(Dense(self.action_space_size))
        self.actionMap = self.createMapping()

        memory = SequentialMemory(limit=50000, window_length=1)
        policy = BoltzmannQPolicy()
        self.dqn = DQNAgent(model=model, processor=MyProcessor(),nb_actions=self.action_space_size, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
        self.dqn.compile(Adam(lr=1e-3), metrics=['mae'])
        #model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate), metrics=['accuracy'])
        # if os.path.isfile(self.weight_backup):
        #     model = load_model(self.weight_backup)
        #     self.exploration_rate = self.exploration_min
        return model

    def calculateActionFromIndex(self, index):
        result ={}
        semiAction=self.actionMap[index]
        result[0]=int(semiAction[0])
        result[1]=int(semiAction[1])
        result[2]=int(semiAction[2])
        return result

    def save_model(self):
        self.brain.save(self.weight_backup)

    def getRandomAction(self, observation):
        result={}
        spacesLength=len(self.action_space.spaces)
        for index in range(0, spacesLength):
            result[index]=random.randint(0, self.action_space.spaces[index].n-1)
        return result

    def run(self, env):
        callback = [MyAgentCallback()]
        self.dqn.fit(env, 5, visualize=True, verbose=2, callbacks=callback, start_step_policy=self.getRandomAction)

    #     if np.random.rand() <= self.exploration_rate:
    #         result={}
    #         spacesLength=len(self.action_space.spaces)
    #         for index in range(0, spacesLength):
    #             result[index]=random.randint(0, self.action_space.spaces[index].n-1)
    #         return result
    #     act_values = self.brain.predict(state)
    #     maxValueIndex = np.argmax(act_values)
    #     return self.calculateActionFromIndex(maxValueIndex)

    # # Updates the Q Table
    # def remember(self, state, new_state, reward):
    #     highest_action_value = np.argmax(self.brain.predict(state))
    #     target = reward + ((self.gamma) * np.max(self.brain.predict(new_state)))
    #     target_vec = self.brain.predict(state)[0]
    #     target_vec[highest_action_value] = target
    #     self.brain.fit(state, target_vec.reshape(-1, self.action_space_size), epochs=1, verbose=0)
    #     if self.exploration_rate > self.exploration_min:
    #         self.exploration_rate *= self.exploration_decay