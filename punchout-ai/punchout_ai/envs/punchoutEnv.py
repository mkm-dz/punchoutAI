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
            "opponent_id": spaces.Discrete(20),
            "opponent_action": spaces.Discrete(256),
            "opponentTimer": spaces.Discrete(256),
            "secondary_opponent_action": spaces.Discrete(256),
            "hearts": spaces.Discrete(60),
            "stars": spaces.Discrete(20),
            "blinkingPink": spaces.Discrete(2),
            "bersekerAction": spaces.Discrete(256)
        })

        # Setting actions to be integers from 0 to 60, 60 matching the result array
        # from punchoutUtils mapping
        self.action_space = spaces.Box(low=np.array([0]),high= np.array([60]), dtype=np.int)

        # We do the dimension definition in here. Then we iterate through the
        # spaces to define the final shape. We could do the full square matrix
        # but that would take more space that is currently not required.
        
        space_length = 0
        for item in self.observation_space.spaces.values():
            space_length = space_length + item.n

        self.observation_space.n = space_length
        self.action_space.n = self.action_space.high[0]
        self.initServer()

    def step(self, action_index):
        agentAction = self.punchUtils.calculateActionFromIndex(action_index)

        # Send the buttons, and wait to see what happened (observation)
        _next_state = self.sendActionToEmulator(agentAction)
        observation = self.punchUtils.castEmuStateToObservation(_next_state, self.observation_space)
        reward = self.computeReward(_next_state)
        done = self.computeDone(_next_state)
        if(done):
            if (_next_state.result=='1'):
                reward+=30
            elif(_next_state.result=='2'):
                reward += -50

        return observation, reward, done, {}

    def reset(self):
        self.previousScore = 0
        self.previousHealth = 96
        self.previousHearths = -1000
        self.punchUtils.sendCommand('reset')
        rawObservation = self.WaitForServer()
        castedObservation = self.punchUtils.castEmuStateToObservation(rawObservation, self.observation_space)
        return castedObservation

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
        blinkingPink = observation.p1['blinkingPink']
        if(self.previousHearths == -1000):
            self.previousHearths = observation.p1['hearts']
        didMacHit = observation.p1['score']-self.previousScore
        wasMacHit = observation.p1['health']-self.previousHealth
        hearthWasLost = observation.p1['hearts']-self.previousHearths
        if (didMacHit > 0):
            result += 5
            # You get more points for star punches
            if(didMacHit > 3):
                result += 5
                # You get even more for landed uppercuts
                if(didMacHit > 30):
                    result += 5
            didMacHit = 0

        if(wasMacHit < 0):
            result += -5
            # It is even worst if we get hit when flashing pink
            if(blinkingPink == 1):
                result += -5
        elif(wasMacHit > 0):
            result += 5
        elif(wasMacHit == 0 and hearthWasLost >= 0):
            # Mac avoided being hit
            result += 1
        wasMacHit = 0

        if(hearthWasLost < 0):
            result += -3
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
        observation = self.punchUtils.castEmuStateToObservation(emuState, self.observation_space)
        return observation

    def sendActionToEmulator(self, action):
        actionButtons = self.punchUtils.castAgentActionToEmuAction(action)
        self.punchUtils.sendCommand('buttons', actionButtons)
        _new_state = self.WaitForServer()
        return _new_state