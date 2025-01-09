#!/bin/python

import json
import sys
from datetime import datetime
import time

######################################
# Reading Config, Starting Runners   #
######################################

#Loading Config
configPath = "SensorNetworkConfig.json"

if len(sys.argv) > 1:
    configPath = sys.argv[1]

with open(configPath,'r') as configFile:
    config = json.load(configFile)

#Utility for Logging:

logFile = open(config["General"]["LogFile"],"a")

def log(text,endSequence="\n"):
    logFile.write(str(datetime.now())+": "+text+endSequence)

#Starting Runners
log("Supervisor Started.")

from ShellyPlugRunner import Runner as ShellyPlugRunner
from AirQRunner import Runner as AirQRunner

#The look up strings here have to match the name of
#the coressponding areas in the config.json
RunnerLookUp = {
        "ShellyPlugs":ShellyPlugRunner,
        "AirQs":AirQRunner
        }

activeRunners = []
activeThreads = []

for RunnerName in RunnerLookUp:
    if RunnerName in config:
        RunnerConstructor = RunnerLookUp[RunnerName]
        
        for instanceName in config[RunnerName]:
            runner = RunnerConstructor(config["General"], 
                                       instanceName, #name of runner and sql table
                                       log, #logger as lambda
                                       **config[RunnerName][instanceName])

            runner.start()
            activeRunners.append(runner)

#########################################
# Supervision of Runners during Runtime #
#########################################

#In this section of the code, we check, id threads are still online.
#If a thread has crashed, and the last crash of this thread has not occured in the last few minutes,
#a new one will be started in this while loop. In any case, an entry in the logs will be written.

timeThreshold = 300 # time in seconds that a thread has to run sucsessful to be restarted in the case of a crash.
lastTimeStarted = [0]*len(activeRunners)
startAgain = [True]*len(activeRunners)#initilized this way because immutable

for i in range(0,len(lastTimeStarted)):
    lastTimeStarted[i] = datetime.now()

while(True):
    time.sleep(10) #sleep for 10 s
    
    for i,runner in enumerate(activeRunners):
        
        if not runner.isAlive():
            crashTime = datetime.now() #discovered crash time
            aliveTime = crashTime-lastTimeStarted

            if aliveTime.total_seconds() < timeThreshold:
                #do not start new thread
                startAgain[i] = False
                log("Runner "+runner.getName()+" has crashed and won't be started again due to small time since last start ( ~"+str(aliveTime.total_seconds())+" s ).")

            if startAgain[i]:
                log("Crash of Runner "+runner.getName()+" detected. Attempting Restart.")
                runner.start()
                lastTimeStarted[i] = datetime.now()


######################################
# Stopping process, stopping runners #
######################################
import atexit

def stopRunnerThreads():
    for runner in activeRunners:
        runner.stop()
       
    log("Stopped Supervisor Process.")
    logFile.close()

atexit.register(stopRunnerThreads)
