import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding
from classes.bizhawkServer import BizHawkServer
from classes.punchUtils import punchUtils

class punchoutAIEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    currentState = None
    previousScore = 0
    previousHealth = 0
    previousHearths = -1000

    def __init__(self):
        self.server = BizHawkServer()
        self.punchUtils = punchUtils()
        self._observation = []
        self.observation_space = spaces.Dict({
            "opponent_id": spaces.Discrete(255),
            "opponent_action": spaces.Discrete(255),
            "opponentTimer": spaces.Discrete(255),
            "secondary_opponent_action": spaces.Discrete(255),
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
        self.initServer()

    def step(self, action):
        if action.envCommand == 'resume':

            # Opponent just started an action, there is no reward for reacting.
            return self.resumeStep(), 0, False, {}

        elif action.envCommand == 'sendButtons':

            # Send the buttons, and wait to see what happened (observation)
            _next_state = self.sendActionToEmulator(action.agentAction)
            observation = self.punchUtils.castEmuStateToObservation(_next_state)
            observation = np.reshape(observation, [1, self.observation_space.n])
            reward = self.computeReward(_next_state)
            done = self.computeDone(_next_state)
            return observation, reward, done, {}

    def reset(self):
        self.previousScore = 0
        self.previousHealth = 96
        self.previousHearths = -1000
        self.punchUtils.sendCommand('reset')
        self.WaitForServer()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self, mode='human', close=False):
        pass

    def initServer(self):
        self.server.start()
        while(self.server.ready == False):
            pass

    def WaitForServer(self) -> str:
        while(self.server.publicState == None):
            pass
        tempState = self.server.publicState
        self.server.publicState = None
        return tempState

    def computeReward(self, observation):
        result = 0
        canThrowPunches = observation.p1['canThrowPunches']
        if(self.previousHearths == -1000):
            self.previousHearths = observation.p1['hearts']
        didMacHit = observation.p1['score']-self.previousScore
        wasMacHit = observation.p1['health']-self.previousHealth
        hearthWasLost = observation.p1['hearts']-self.previousHearths
        if (didMacHit > 0):
            result += 5
            didMacHit = 0

        if(wasMacHit < 0):
            result += -5
        elif(wasMacHit > 0):
            result += 5
        elif(wasMacHit == 0 and canThrowPunches != 0):
            # Mac avoided being hit
            result += 1
        wasMacHit = 0

        if(hearthWasLost < 0):
            result += -5
        elif(hearthWasLost > 0):
            result += 5
        hearthWasLost = 0

        # This can be considered the last method so we
        # set the previousScore in here
        self.previousScore = observation.p1['score']
        self.previousHealth = observation.p1['health']
        self.previousHearths = observation.p1['hearts']
        return result

    def computeDone(self, observation):
        if(observation.round_over == True):
            return True
        else:
            return False

    def resumeStep(self):
        self.punchUtils.sendCommand('resume', None)

        # Wait for opponent to initiate action
        emuState = self.WaitForServer()
        observation = self.punchUtils.castEmuStateToObservation(emuState)
        return np.reshape(observation, [1, self.observation_space.n])

    def sendActionToEmulator(self, action):
        actionButtons = self.punchUtils.castAgentActionToEmuAction(action)
        self.punchUtils.sendCommand('buttons', actionButtons)
        _new_state = self.WaitForServer()
        return _new_state