
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
        self.action_dim = action_space.n
        self.action_space = action_space
        self.memory = deque(maxlen=2000)
        self.learning_rate = 0.001
        self.gamma = 0.95
        self.exploration_rate = 1.0
        self.exploration_min = 0.01
        self.exploration_decay = 0.995
        self.brain = self._build_model()

    def custom_activation(self, x):
        x = K.tanh(x)
        return x

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_dim, activation=self.custom_activation))

        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        if os.path.isfile(self.weight_backup):
            model.load_weights(self.weight_backup)
            self.exploration_rate = self.exploration_min
        return model
    
    def massageDataPad(self, data, max_value):
        range_size=2/(max_value)
        pivot=-1
        for index in range(0,(max_value)):
            if(data>=pivot and data<=pivot+range_size):
                return index
            else:
                pivot += range_size
        return max_value-1

    def calculateAction(self,data):
        result={}
        # 0: buttons
        # 1: pads
        result[0]=self.massageDataPad(data[0],self.action_space.spaces[0].n)
        result[1]=self.massageDataPad(data[1],
        self.action_space.spaces[1].n)
        return result

    def save_model(self):
            self.brain.save(self.weight_backup)

    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            result={}
            for index in range(0,self.action_dim):
                result[index]=random.randint(0, self.action_space.spaces[index].n-1)
            return result
        act_values = self.brain.predict(state)[0]
        return self.calculateAction(act_values)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, sample_batch_size):
        if len(self.memory) < sample_batch_size:
            return
        sample_batch = random.sample(self.memory, sample_batch_size)
        target=None
        casted_action={}
        for state, action, reward, next_state, done in sample_batch:
            if(target==None):
                target=reward
            act_values=self.brain.predict(state)[0]
            if(reward>=target):
                act_values=self.brain.predict(next_state)[0]

        for state, action, reward, next_state, done in sample_batch:
            casted_action={}
            casted_action[0]=act_values[0]
            casted_action[1]=act_values[1]
            calculatedValues=self.calculateAction(casted_action)
            target_f = self.brain.predict(state)

            if done:
                calculatedValues[0]=action[0]
                calculatedValues[1]=action[1]
            target_f[0][0] = calculatedValues[0]
            target_f[0][1] = calculatedValues[1]
            self.brain.fit(state, target_f, epochs=1, verbose=0)

        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay
