import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding


class punchoutAIEnv(gym.Env):
  metadata = {'render.modes': ['human']}
  lastState = None

  def __init__(self):
    self._observation = []
    self.observation_space = spaces.Dict({
        "self_health": spaces.Discrete(255),
        "opponent_health": spaces.Discrete(255),
        "opponent_action": spaces.Discrete(255),
        "in_move": spaces.Discrete(2),
        "round_over": spaces.Discrete(2),
        "result": spaces.Discrete(2),
    })

    self.action_space = spaces.Tuple([
        # The first array is the lowest accepted values
        # The second is the highest accepted values
        # [0,4] None, Up, Right, Down, Left
        # [0,2] None, A, B
        spaces.Discrete(2),
        spaces.Discrete(4),
    ])

    self.observation_space.n = len(self.observation_space.spaces)
    self.action_space.n = len(self.observation_space.spaces)

  def step(self, action):
    self._observation = self.computeState()
    reward = self.computeReward()
    done = self.computeDone()
    return self._observation, reward, done, {}

  def reset(self):
      return self.computeState()

  def seed(self, seed=None):
    self.np_random, seed = seeding.np_random(seed)
    return [seed]

  def render(self, mode='human', close=False):
    pass

  def setState(self, object):
    self.lastState = object
    
  def computeState(self):
    castedSpaces = spaces.Dict({
        'self_health': self.lastState.p1.health,
        'opponent_health': self.lastState.p2.health,
        'opponent_action': self.lastState.p2.action,
        'in_move': self.lastState.p2.InMove,
        'round_over': self.lastState.round_over,
        'result': self.lastState.result,
    })
    return np.fromiter(castedSpaces.spaces.values(), dtype=int)

  def computeReward(self):
        if(self.lastState.round_over == True):
            if(self.lastState.result == 'P1'):
                return 100
            elif(self.lastState.result == 'P2'):
                return -100
            else:
                raise ValueError('Should never get here')
        else:
            return self.lastState.p1.health-self.lastState.p2.health

  def computeDone(self):
        if(self.lastState.round_over == True):
            return True
        else:
            return False
