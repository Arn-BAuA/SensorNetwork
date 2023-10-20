# Sensor Network SQL Allocator

This is a program that is ment to run a sensor network with the following(ish) topology:
TODO: Make Picture.

## Intorduction
The idea here is relatively simple. The program at hand is ment to be run on the server in a sensor network to cover gather the information that is available in diffrent spots in the network and save them in the SQL database. The program consists of one supervisor script (Supervisor.py). The supervisor takes one flag, that should contain a path that points to the SensorNetworkConfig.json file, that has the informations on the sensor network that should be ran (where are which rescources).<br>
It than creates one Runner instance for every resource. Runners are programms that each have their own sub process and are attached to one data source. If there are e.g. 2 AirQ sensorstations and 6 Shelly Plugs, there is one supervisor process and 8 runners. 2 for the individual airQs and 6 for the individual shellys.<br>
The Runners basically capture or request data and store it in the database. In the case of the shelly plug, the runner listens to the MQTT topics of its shelly plug and, upon arriving messages, stores the data in the SQL database.<br>
The AirQ-Runner works a little bit different. The AirQ provides data on a http-server. The runner requests that data every n seconds and stores it.
Runners inheret from the global runner class, that contains coder to unify the way, informations are passed trough the runners in the config.json and the interaction with the sql.

## Config.json and general Runner interface.

The config.json has multiple areals. One is the general field. General information on the sensor net, like address, port and database name of the database are contained here.
Per kind of runner that is used, a nother area has to be defined. The name of this area is runner specific. e.g. AirQ for the airQ-runners.
In this areal are different subsections. One per runner. The all contain the information that is needet for the SQL-Storage (name of the table to store data in). The field is named "Table Name". They also must contain a field named "RescouceInfo" That contains data source specific info that is needet to access the rescouce. In the case of the shelly plug these infos are the name of the shelly plug to identify the MQTT topic.
The handling of these informations is automatically done by the runner.py parent class. The child classes just have to implement specific parts and get specific informations passed directly.

## Running the Sensor Network

## Different Runner instances

### AirQ Runner

### Shelly Plug Runner

## Setting up the Network.
