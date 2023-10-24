
from MQTTRunner import Runner as MQTTRunner
from datetime import datetime

class Runner(MQTTRunner):

    def __init__(self,generalInfo,name,logger,**config):
        topics = [
               "shellies/shellyplug-"+config["PlugName"]+"/relay/0",#on / off
               "shellies/shellyplug-"+config["PlugName"]+"/relay/0/power",#power consumption
                ];
        
        #Idea here, the Shelly reports both topics at more or less the same time.
        #Both will be collected in this data structure.
        #If all is clollected it will be reported at once.
        self.recivedMessages = 0

        MQTTRunner.__init__(self,generalInfo,name,logger,topics)
    
    def _getTableColumns(self):
        columns = {
         "time":"DATETIME",
         "online":"BOOLEAN",
         "power":"INT",
        }
        return columns

    def _on_message(self,client,userdata,message):
        
        if message.topic == self.topics[0]:
            self.onlineMessage = message
        if message.topic == self.topics[1]:
            self.powerMessage = message

        print(message.topic)
        self.recivedMessages += 1
        
        if self.recivedMessages >= 2:
            #blog in
            insertQuery = "INSERT INTO "+self.name+" VALUES ("
            #insertQuery +=datetime.now().strftime("%Y-%m-%d %H:%M:%S")+", "
            insertQuery +="NOW(), "
            
            online =str(self.onlineMessage.payload)[2:-1]
            if online == "on":
                insertQuery +="TRUE, "
            else:
                insertQuery +="FALSE, "

            insertQuery +=str(self.powerMessage.payload)[2:-1]
            insertQuery +=");"
            
            print(insertQuery)

            self.cursor.execute(insertQuery)
            
            self.recivedMessages = 0
