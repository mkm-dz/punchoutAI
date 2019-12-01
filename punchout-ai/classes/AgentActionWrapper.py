class AgentActionWrapper:
    def __init__(self):
        self.agentAction = None
        self.envCommand = None

    def __add__(self, anotherWrapper):
        # Needed for verbose callbacks
        return self

    def __truediv__(self, other):
        # Needed for verbose callbacks
        return self

    def __le__(self, other):
        # Needed for verbose callbacks
        return self

    def __format__(self, other):
        # Needed for verbose callbacks
        return "none"
