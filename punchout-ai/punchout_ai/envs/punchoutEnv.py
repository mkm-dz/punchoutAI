import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding

class punchoutAIEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self._observation=[]
    self.observation_space = spaces.Dict({
        "self_health": spaces.Discrete(255),
        "opponent_health": spaces.Discrete(255),
        "opponent_action": spaces.Discrete(255),
        "in_move": spaces.Discrete(2),
        "round_over": spaces.Discrete(2),
        "result": spaces.Discrete(2),
    })

    self.action_space = spaces.Box(
        # The first array is the lowest accepted values
        # The second is the highest accepted values
        # [0,4] None, Up, Right, Down, Left
        # [0,2] None, A, B
        np.array([0,0]),
        np.array([4,2]),
    )

    self.seed()

  def step(self, action):
    self._observation = self._compute_observation(action)

  def reset(self):
    pass

  def seed(self, seed=None):
    pass

  def render(self, mode='human', close=False):
    pass
    
  def _compute_observation(self, action):
    return spaces.Dict({
        "self_health": action.p1.health,
        "opponent_health": action.p2.health,
        "opponent_action": action.p2.action,
        "in_move": action.p2.InMove,
        "round_over": action.round_over,
        "result": action.result,
    })