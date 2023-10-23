
import paho.mqtt.client as mqtt
import time


#THis is the MQTT Runner. The way this works is that the runner implements the 
# client interface from the paho mqtt library.
# it creates and runs a client, that automatically blogs in messages on recieving.
# The topics get passed from the constructor of the subclass.
# Instead of _on_Execution, the subclasses have to overwrite the _on_Message_Recived
# method, which gets passed to the client.
class Runner(RunnerBase):

    def __init__(self,generalInfo,name,logger,topics,**config):
        RunnerBase.__init__(self,generalInfo,name,logger)
        
        self.topics = topics
        self.MQTTIP = generalInfo["MQTT_IP"]
        self.MQTTPort = generalInfo["MQTT_Port"]

    #Has to be overwritten.
    def _on_message(client,userdata,message):
        pass

    def _on_Execution(self):
        
        self.client = client()
        self.client.on_message = self._on_message

        try
            self.client.connect(self.MQTTIP,self.MQTTPort,60)
        except(e):
            self.log("Error in Runner \""+self.name+"\". "+e)

        self.client.loopstart()

        for topic in self.topics:
            client.subscribe(topic,2)

        while not self.recivedHaltSignal:
            sleep(1)
