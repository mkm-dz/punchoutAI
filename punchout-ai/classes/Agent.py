
import gym
import random
import os
import numpy as np

from collections import deque
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense
from keras.optimizers import Adam
from keras import backend as K

class Agent():

    brain=None
    def __init__(self, state_size, action_space):
        self.weight_backup = "VonKaiser.h5py"
        self.state_size = state_size
        self.action_space =  action_space
        self.action_space_size = 1
        for index in range(0, action_space.n):
            self.action_space_size *= action_space.spaces[index].n
        self.learning_rate = 0.005
        self.gamma = 0.95
        self.exploration_rate = 1.0
        self.exploration_min = 0.30
        self.exploration_decay = 0.999
        self.brain = self._build_model()

    def createMapping(self):
        # We have an output space of 15 possible actions (moves)
        # we map each one to a controller action
        result={}
        result[0] = '00'
        result[1] = '01'
        result[2] = '02'
        result[3] = '03'
        result[4] = '04'
        result[5] = '10'
        result[6] = '11'
        result[7] = '12'
        result[8] = '13'
        result[9] = '14'
        result[10] = '20'
        result[11] = '21'
        result[12] = '22'
        result[13] = '23'
        result[14] = '24'
        return result


    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(self.state_size, input_dim=self.state_size, 
        activation='relu'))
        model.add(Dense(self.action_space_size + 2, activation='relu'))
        model.add(Dense(self.action_space_size, activation='relu'))
        model.add(Dense(self.action_space_size))
        self.actionMap = self.createMapping()

        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate), metrics=['accuracy'])
        if os.path.isfile(self.weight_backup):
            model = load_model(self.weight_backup)
            self.exploration_rate = self.exploration_min * 2
        return model

    def calculateActionIndex(self,action):
          value=('%s%s' % (action[0],action[1]))
          mapIndex=list(self.actionMap.keys())[list(self.actionMap.values()).index(value)]
          return mapIndex

    def calculateActionFromIndex(self, index):
        result ={}
        semiAction=self.actionMap[index]
        result[0]=int(semiAction[0])
        result[1]=int(semiAction[1])
        return result

    def save_model(self):
        self.brain.save(self.weight_backup)

    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            result={}
            spacesLength=len(self.action_space.spaces)
            for index in range(0, spacesLength):
                result[index]=random.randint(0, self.action_space.spaces[index].n-1)
            return result
        act_values = self.brain.predict(state)
        maxValueIndex = np.argmax(act_values)
        return self.calculateActionFromIndex(maxValueIndex)

    # Updates the Q Table
    def remember(self, state, new_state, reward):
        highest_action_value = np.argmax(self.brain.predict(state))
        target = reward + ((self.gamma) * np.max(self.brain.predict(new_state)))
        target_vec = self.brain.predict(state)[0]
        target_vec[highest_action_value] = target
        self.brain.fit(state, target_vec.reshape(-1, self.action_space_size), epochs=1, verbose=0)
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay