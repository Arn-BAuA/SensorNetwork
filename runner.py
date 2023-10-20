
import threading

#base class of all runners.
class RunnerBase:

    def __init__(self,sqlIP,sqlPort,dbName,tableName):
        pass
    
    #This gets called by start() and has to be overwritten.
    def _on_Execution(self):
        pass

    #This is the method that gets started by the supervisor
    #Communication is initailized here, necessairy dbs and tables are created.
    #The tread for the runner is created here.
    def start(self):
        pass

    def stop(self):
        pass

