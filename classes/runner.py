import gym

class RunWrapper:
    runnerEnv=None
    def __init__(self, env: gym.Env):
        self.runnerEnv = env
    def SendData(self):
        #send data in here
        pass