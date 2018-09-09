from gym.envs.registration import register

register(
    id='punchoutAI-v0',
    entry_point='punchout_ai.envs:punchoutAIEnv',
)