import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding


class punchoutAIEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self._observation = []
    # self.observation_space = spaces.Dict({
    #     "self_health": spaces.Discrete(255),
    #     "opponent_health": spaces.Discrete(255),
    #     "opponent_action": spaces.Discrete(255),
    #     "in_move": spaces.Discrete(2),
    #     "round_over": spaces.Discrete(2),
    #     "result": spaces.Discrete(2),
    # })

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

    self.observation_space.n =len(self.observation_space.spaces)
    self.action_space.n =len(self.observation_space.spaces)

  def step(self, action):
    self._observation = self._compute_observation(action)
    return self._observation, 0.6, False, {}

  def reset(self):
      #send reset to emulator and get initial observation
      return self._compute_observation(None)

  def seed(self, seed=None):
    self.np_random, seed = seeding.np_random(seed)
    return [seed]

  def render(self, mode='human', close=False):
    pass

  def _compute_observation(self, action):
    testSpaces =  spaces.Dict({
        "self_health": 100,
        "opponent_health": 100,
        "opponent_action": 2,
        "in_move": 1,
        "round_over": 0,
        "result": 0,
    })
    return np.fromiter(testSpaces.spaces.values(), dtype=int)
