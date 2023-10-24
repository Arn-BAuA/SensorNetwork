
import paho.mqtt.client as mqtt
import time
from runner import RunnerBase

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
        self.MQTTPort = int(generalInfo["MQTT_Port"])

    #Has to be overwritten.
    def _on_message(self,client,userdata,message):
        pass

    def _on_Execution(self):
        
        self.client = mqtt.Client()
        self.client.on_message = self._on_message

        try:
            self.client.connect(self.MQTTIP,self.MQTTPort,60)
        except Exception as e:
            self.log("Error in Runner \""+self.name+"\". "+str(e))

        self.client.loop_start()

        for topic in self.topics:
            self.client.subscribe(topic,2)

        while not self.recivedHaltSignal:
            time.sleep(1)
