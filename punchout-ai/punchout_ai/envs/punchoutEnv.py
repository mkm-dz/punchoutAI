import gym
from gym import error, spaces, utils
from gym.utils import seeding

class punchoutAIEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.observation_space = spaces.Dict({
        "self_health": spaces.Discrete(255),
        "opponent_health": spaces.Discrete(255),
    })

    self.action_space = spaces.MultiDiscrete([
        [0,4], #None, Up, Right, Down, Left
        [0,6], #None, A, B, X, Y, L ,R
    ])

  def step(self, action):
    pass

  def reset(self):
    pass

  def seed(self, seed=None):
    pass

  def render(self, mode='human', close=False):
    pass
