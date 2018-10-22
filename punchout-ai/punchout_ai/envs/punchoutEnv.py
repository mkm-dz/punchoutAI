import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding


class punchoutAIEnv(gym.Env):
  metadata = {'render.modes': ['human']}
  currentState = None
  previousScore=0

  def __init__(self):
    self._observation = []
    self.observation_space = spaces.Dict({
        "opponent_id": spaces.Discrete(255),
        "opponent_action": spaces.Discrete(255),
        "opponentTimer": spaces.Discrete(255),
        "round_over": spaces.Discrete(2),
        "hearts": spaces.Discrete(255),
        "result": spaces.Discrete(3),
        "canThrowPunches": spaces.Discrete(2)
    })

    self.action_space = spaces.Tuple([
        # The first array is the lowest accepted values
        # The second is the highest accepted values
        # [0,2] None, A, B
        # [0,4] None, Up, Right, Down, Left
        spaces.Discrete(3),
        spaces.Discrete(5),
    ])

    self.observation_space.n = len(self.observation_space.spaces)
    self.action_space.n = len(self.action_space.spaces)

  def step(self, action):
    self._observation = self.computeState(self.currentState)
    reward = self.computeReward()
    done = self.computeDone()
    return self._observation, reward, done, {}

  def reset(self):
      self.previousScore=0
      return self.computeState(self.currentState)

  def seed(self, seed=None):
    self.np_random, seed = seeding.np_random(seed)
    return [seed]

  def render(self, mode='human', close=False):
    pass

  def setState(self, object):
    self.currentState = object

  def computeState(self, state):
    castedSpaces = spaces.Dict({
        'opponent_id': state.p2['character'],
        'opponent_action': state.p2['action'],
        'opponentTimer': state.p2['actionTimer'],
        'round_over': state.round_over,
        'hearts': state.p1['hearts'],
        'result': state.result,
        'canThrowPunches': state.p1['canThrowPunches']
    })
    return np.fromiter(castedSpaces.spaces.values(), dtype=int)

  def computeReward(self):
    extra=0
    # if(self.currentState.round_over == True):
    #     if(self.currentState.result == '1'):
    #         extra = 500
    #     elif(self.currentState.result == '2'):
    #         extra = -500
    #     else:
    #         raise ValueError('Should never get here')

    didMacHit=self.currentState.p1['score']-self.previousScore
    if (didMacHit > 0):
        extra+=200
        didMacHit=0
    result = extra + ((self.currentState.p1['health']-self.currentState.p2['health'])*3)+(self.currentState.p1['hearts']*3) +(self.currentState.p1['score']*5)

    # This can be considered the last method so we 
    # set the previousScore in here
    self.previousScore=self.currentState.p1['score']
    return result

  def computeDone(self):
        if(self.currentState.round_over == True):
            return True
        else:
            return False
