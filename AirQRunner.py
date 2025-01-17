
from runner import RunnerBase

import time

import base64
import json
from Crypto.Cipher import AES
import http.client

class Runner(RunnerBase):

    def __init__(self,generalInfo,name,logger,**config):
        RunnerBase.__init__(self,generalInfo,name,logger)

        self.AirQIP = config["IP"]
        self.AirQPass = config["PW"]
        if "MeasurementFreq." in config:
            self.measurementFrequency = config["MeasurementFreq."]
        else:
            self.measurementFrequency = 10
    
    def requestMessage(self):

        def unpad(data):
            return data[:-ord(data[-1])]

        def decodeMessage(msgb64):
            msg=base64.b64decode(msgb64)
            key = self.AirQPass.encode('utf-8')
            if len(key)<32:
                for i in range(32-len(key)):
                    key += b'0'
            elif len(key) > 32:
                key = key[:32]

            cipher= AES.new(key=key,mode=AES.MODE_CBC,IV=msg[:16])
            return unpad(cipher.decrypt(msg[16:]).decode('utf-8'))
        
        succsess = False
        retryTimer = 50

        while not succsess:
            try:
                connection = http.client.HTTPConnection(self.AirQIP)
                connection.request("GET","/data")
                contents = connection.getresponse()
                connection.close()
                succsess = True
            except:
                pass

            if not succsess:
                #If connection failed, the thing will just wait.
                time.sleep(retryTimer)


        msg =  json.loads(contents.read())
        msg['content'] = json.loads(decodeMessage(msg['content']))

        return msg['content']



    def _getTableColumns(self):

        columns = {
                "time": "TIMESTAMP",##################
                "tvoc":"INT",
                "delta_tvoc":"INT",###################
                "pm2_5": "INT",
                "delta_pm2_5": "INT",#################
                "humidity": "DOUBLE",
                "delta_humidity": "DOUBLE",###########
                "cnt0_3": "INT",
                "delta_cnt0_3": "INT",################
                "measuretime": "INT",#################
                "sound": "DOUBLE",
                "delta_sound":"DOUBLE",###############
                "temperature":"DOUBLE",
                "delta_temperature":"DOUBLE",#########
                "cnt0_5": "INT",
                "delta_cnt0_5": "INT",################
                "performance": "DOUBLE",##############
                "co": "DOUBLE",
                "delta_co": "DOUBLE",#################
                "humidity_abs": "DOUBLE",
                "delta_humidity_abs": "DOUBLE",#######
                "co2": "DOUBLE",
                "delta_co2": "DOUBLE",################
                "uptime": "INT",######################
                "so2": "DOUBLE",
                "delta_so2": "DOUBLE",################
                "cnt2_5": "INT",
                "delta_cnt2_5": "INT",################
                "o3": "DOUBLE",
                "delta_o3": "DOUBLE",#################
                "cnt10": "INT",
                "delta_cnt10": "INT",#################
                "no2": "DOUBLE",
                "delta_no2": "DOUBLE",################
                "cnt5": "INT",
                "delta_cnt5": "INT",##################
                "h2s": "DOUBLE",
                "delta_h2s": "DOUBLE",################
                "TypPS": "DOUBLE",####################
                "pressure": "DOUBLE",
                "delta_pressure": "DOUBLE",###########
                "sound_max": "DOUBLE",
                "delta_sound_max": "DOUBLE",##########
                "pm1": "INT",
                "delta_pm1":"INT",####################
                "oxygen": "DOUBLE",
                "delta_oxygen": "DOUBLE",#############
                "cnt1": "INT",
                "delta_cnt1": "INT",##################
                "dewpt": "DOUBLE",
                "delta_dewpt": "DOUBLE",##############
                "pm10": "INT",
                "delta_pm10": "INT",##################
                "health": "INT"}######################

        self.createdColumns = columns
        return columns

    def _on_Execution(self):
        while not self.recivedHaltSignal:
            
            time.sleep(self.measurementFrequency)
            
            AirQData = self.requestMessage()
            
            columns = ""
            values = ""

            for key in AirQData:
                if not key in self.createdColumns:
                    continue
                if type(AirQData[key]) == list:
                    #This means there is a value and an uncertainty
                    columns+=key+", "
                    values +=str(AirQData[key][0])+", " 
                    columns+="delta_"+key+", "
                    values +=str(AirQData[key][1])+", " 
                else:
                    columns+=key+", "
                    values +=str(AirQData[key])+", " 
           
            values = values[:-2] #removing the last ' ,'
            columns = columns[:-2] #removing the last ' ,'

            insertQuery = "INSERT INTO "+self.name+" ("+columns+") VALUES ("+values+");"
            self.cursor.execute(insertQuery)
            self.connection.commit()

