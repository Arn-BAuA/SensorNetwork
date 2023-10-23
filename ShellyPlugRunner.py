
from runner import RunnerBase

class Runner(RunnerBase):

    def __init__(self,generalInfo,name,logger,**config):
        RunnerBase.__init__(self,generalInfo,name,logger)
    
    def _on_Execution(self):
        while not self.recivedHaltSignal:
            pass

