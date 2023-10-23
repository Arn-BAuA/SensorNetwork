
import threading

#base class of all runners.
class RunnerBase:

    def __init__(self,generalInfo,name,logMethod):
        self.sqlIP = generalInfo["SQLAddress"]
        self.sqlPort = generalInfo["SQLPort"]
        self.dbName = generalInfo["SQLDBName"]
                                       
        self.name = name

        self.log = logMethod
        
        #is used to stop thread
        self.recivedHaltSignal=False
    
    #This gets called by start() and has to be overwritten.
    #It is assumend, that this contains a loop that runs until
    # recivedHaltSignal is True.
    def _on_Execution(self):
        pass
    
    #Checks if DB is present and if not, creates it.
    def __initializeDB(self):
        pass

    #Checks if table is present and if not, creates it.
    def __initializeTable(self):
        pass
    
    #starting to talk to sql db
    def __initializeCommunication(self):
        pass
    
    #ending the communication with the sql
    def __endCommunication(self):
        pass

    #This is the method that gets started by the supervisor
    #Communication is initailized here, necessairy dbs and tables are created.
    #The tread for the runner is created here.
    def start(self):
        
        def threadJob():
            self.__initializeCommunication()
            self._on_Execution()
            self.__endCommunication()
        
        self.thread=threading.Thread(target=threadJob)
        self.thread.start()
        self.log("Runner \""+self.name+"\" Started")

    def stop(self):
        self.recivedHaltSignal = True
        self.thread.join()
        self.log("Runner \""+self.name+"\" Stopped")

