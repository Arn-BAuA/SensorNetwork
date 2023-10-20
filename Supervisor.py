#!/bin/python

import json
import sys
from datetime import datetime

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
            runner = RunnerConstructor(
                                       config["General"]["SQLAddress"], 
                                       config["General"]["SQLPort"], 
                                       config["General"]["SQLDBName"], 
                                       instanceName, #name of sql table
                                       **config[RunnerName][instanceName])

            runner.start()
            activeRunners.append(runner)
            log("Runner \""+instanceName+"\" started.")


######################################
# Stopping process, stopping runners #
######################################
import atexit

def stopRunnerThreads():
    for runner in activeRunners:
        runner.stop()
    
    log("Stopped all Runners.")

atexit.register(stopRunnerThreads)
