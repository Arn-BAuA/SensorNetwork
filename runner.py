
import mariadb
import threading

#base class of all runners.
class RunnerBase:

    def __init__(self,generalInfo,name,logMethod):
        self.sqlIP = generalInfo["SQLAddress"]
        self.sqlPort = int(generalInfo["SQLPort"])
        self.sqlUser = generalInfo["SQLUser"]
        self.sqlPasswd = generalInfo["SQLPassword"]
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
    
    #The columns for the table that should contain the data are
    #returned here, as dict. (Table name and value)
    #This needs to be overwritten, as it is called at the
    #initialisation of the communication.
    def _getTableColumns(self):
        pass

    #starting to talk to sql db
    def __initializeCommunication(self):
        #Start Connertion to DB
        
        try:
            self.connection = mariadb.connect(user = self.sqlUser,
                                             password = self.sqlPasswd,
                                             host = self.sqlIP,
                                             port = self.sqlPort,
                                             database = self.dbName)
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(e)
            self.log("Runner \""+self.name+"\" Failed to connecto to DB:\n"+str(e))

        #Create Table If not there.
        
        createQuery = "CREATE TABLE IF NOT EXISTS "+self.name+" ("
        
        tableColumns = self._getTableColumns()
        for columnName in tableColumns:
            createQuery += " "+columnName+" "+tableColumns[columnName]+","
        createQuery = createQuery[:-1] #removing last ','

        createQuery +=");"

        self.cursor.execute(createQuery)
        

    #ending the communication with the sql
    def __endCommunication(self):
        self.cursor.close()
        self.connection.close()

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
    
    def isAlive(self):
        return self.thread.is_alive()
    
    def getName(self):
        return self.name()

    def stop(self):
        self.recivedHaltSignal = True
        self.thread.join()
        self.log("Runner \""+self.name+"\" Stopped")

