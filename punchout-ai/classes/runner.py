class RunWrapper:
    runnerLastState=None

    def HoldState(self, receivedState: str):
        self.runnerLastState=receivedState