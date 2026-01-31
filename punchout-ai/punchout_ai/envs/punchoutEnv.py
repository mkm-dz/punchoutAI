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
    previousBlinkingPink = 0

    def __init__(self):
        self.server = BizHawkServer()
        self.punchUtils = punchUtils()
        self._observation = []

        # Instead of a Dict with one-hot encoding we used normalized float values
        # Reducing to 15 values instead of 870 bits - much more efficient for DQN
        # State: [opponent_id, opponent_state, hearts, stars, blinkingPink, berserker, 
        #         elapsed_min, elapsed_sec, elapsed_dec, opp_y_pos, opp_sprite1, opp_sprite2, 
        #         opp_next_action_timer, opp_next_action, opp_action_set]
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(15,),
            dtype=np.float32
        )

        # Setting actions to be integers from 0 to 60, 60 matching the result array
        # from punchoutUtils mapping
        # Using  Discrete as DQN requires discrete action space
        self.action_space = spaces.Discrete(60)
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
                # Differentiate KO vs Decision wins
                if (_next_state.p2['health'] == 0):  # KO victory
                    reward += 50
                    # Early KO bonus (max +18 for instant KO)
                    elapsed_total_seconds = _next_state.elapsed_minutes * 60 + _next_state.elapsed_seconds + _next_state.elapsed_decimals / 100.0
                    time_bonus = (180 - elapsed_total_seconds) / 10
                    reward += time_bonus
                else:  # Decision victory
                    reward += 10  # Lower reward for decision wins
            elif(_next_state.result=='2'):
                reward += -50

        return observation, reward, done, {}

    def reset(self):
        self.previousScore = 0
        self.previousHealth = 96
        self.previousHearths = -1000
        self.previousBlinkingPink = 0
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
        blinkingPink = observation.p1['blinkingPink']
        
        # Per-step penalty to encourage faster victories
        result = -0.1
        
        # Being pink is dangerous - extra penalty for vulnerability
        if blinkingPink == 1:
            result += -0.2  # Additional penalty while stunned
        
        # Big reward for successfully recovering from pink state (dodge worked!)
        if self.previousBlinkingPink == 1 and blinkingPink == 0:
            result += 10  # Strong reward for quick recovery
        
        if(self.previousHearths == -1000):
            self.previousHearths = observation.p1['hearts']
        didMacHit = observation.p1['score']-self.previousScore
        wasMacHit = observation.p1['health']-self.previousHealth
        hearthWasLost = observation.p1['hearts']-self.previousHearths

        # Reward for landing punches (scaled by damage)
        if (didMacHit > 0):
            result += 10  # Base punch reward
            # You get more points for star punches
            if(didMacHit > 3):
                result += 5
                # You get even more for landed uppercuts
                if(didMacHit > 30):
                    result += 10  # Uppercut bonus
            didMacHit = 0

        # Penalty for taking damage
        if(wasMacHit < 0):
            result += -8  # Increased penalty
            if(blinkingPink == 1):
                result += -8  # Double penalty if we get hit when flashing pink
        elif(wasMacHit > 0):
            result += 5
        elif(wasMacHit == 0 and hearthWasLost >= 0):
            # Mac avoided being hit
            result += 0.5
        wasMacHit = 0

        # Hearts are critical resources
        if(hearthWasLost < 0):
            result += -10  # Losing heart is very bad (increased from -3)
        elif(hearthWasLost > 0):
            result += 15  # Gaining heart is very good (increased from 5)
        hearthWasLost = 0

        # This can be considered the last method so we
        # set the previousScore in here
        self.previousScore = observation.p1['score']
        self.previousHealth = observation.p1['health']
        self.previousHearths = observation.p1['hearts']
        self.previousBlinkingPink = blinkingPink
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