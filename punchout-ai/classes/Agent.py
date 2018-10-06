
import gym
import random
import os
import numpy as np

from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras import backend as K

class Agent():

    def __init__(self, state_size, action_space):
        self.weight_backup = "cartpole_weight.h5"
        self.state_size = state_size

        self.output_dim = action_space.n
        self.action_space = action_space
        self.memory = deque(maxlen=2000)
        self.learning_rate = 0.001
        self.gamma = 0.95
        self.exploration_rate = 1.0
        self.exploration_min = 0.01
        self.exploration_decay = 0.995
        self.brain = self._build_model()

    def createMapping(self):
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
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        #TODO this should be calculated based on the action permutations not hardcoded.
        model.add(Dense(self.action_space.spaces[0].n * self.action_space.spaces[1].n))
        self.actionMap = self.createMapping()

        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        if os.path.isfile(self.weight_backup):
            model.load_weights(self.weight_backup)
            #self.exploration_rate = self.exploration_min
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
        act_values = self.brain.predict(state)[0]
        maxValueIndex = np.argmax(act_values)

        return self.calculateActionFromIndex(maxValueIndex)

    def remember(self, state, action, reward, next_state, done):
        castedAction=self.calculateActionIndex(action)
        self.memory.append((state, castedAction, reward, next_state, done))

    def replay(self, sample_batch_size):
        if len(self.memory) < sample_batch_size:
            return
        sample_batch = random.sample(self.memory, sample_batch_size)

        for initial_state, action, reward, final_state, done in sample_batch:
            target = self.brain.predict(initial_state)
            if done:
                target[0][action]=reward
            else:
                Q_future = max(self.brain.predict(final_state)[0])
                target[0][action]=reward + Q_future * self.gamma
            self.brain.fit(initial_state, target, epochs=1,verbose=0)

        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay
