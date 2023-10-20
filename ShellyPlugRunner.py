
form runner import RunnerBase

class Runner(RunnerBase):

    def __init__(self,sqlIP,sqlPort,dbName,tableName,**config):
        RunnerBase.__init__(self,sqlIP,sqlPort,dbName,tableName)
        print("Air Q",config)
    
    def _on_Execution(self):
        while not self.recivedHaltSignal:
            pass

