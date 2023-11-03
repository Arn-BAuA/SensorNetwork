
from MQTTRunner import Runner as MQTTRunner

class Runner(MQTTRunner):

    def __init__(self,generalInfo,name,logger,**config):
        topics = [
               "shellies/shellyplug-"+config["PlugName"]+"/relay/0",#on / off
               "shellies/shellyplug-"+config["PlugName"]+"/relay/0/power",#power consumption
                ];
        
        self.onlineMessage = "NULL"
        self.powerMessage = "NULL"

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
            self.onlineMessage = str(message.payload)[2:-1]
        if message.topic == self.topics[1]:
            self.powerMessage =str(message.payload)[2:-1]


        #blog in
        insertQuery = "INSERT INTO "+self.name+" VALUES ("
        insertQuery +="NOW(), "
        
        if self.onlineMessage == "on":
            insertQuery +="TRUE, "
        else:
            insertQuery +="FALSE, "

        insertQuery +=self.powerMessage
        insertQuery +=");"

        self.cursor.execute(insertQuery)
        self.connection.commit()
