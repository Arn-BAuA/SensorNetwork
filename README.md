![](.figures/Banner.png)

This is a program that is ment to run a sensor network with the following(ish) topology:
![](.figures/NetworkOverview.png)

## Intorduction
The idea here is relatively simple. The program at hand is ment to be run on the server in a sensor network to cover gather the information that is available in diffrent spots in the network and save them in the SQL database. The program consists of one supervisor script (Supervisor.py). The supervisor takes one flag, that should contain a path that points to the SensorNetworkConfig.json file, that has the informations on the sensor network that should be ran (where are which rescources).<br>
It than creates one Runner instance for every resource. Runners are programms that each have their own sub process and are attached to one data source. If there are e.g. 2 AirQ sensorstations and 6 Shelly Plugs, there is one supervisor process and 8 runners. 2 for the individual airQs and 6 for the individual shellys.<br>
The Runners basically capture or request data and store it in the database. In the case of the shelly plug, the runner listens to the MQTT topics of its shelly plug and, upon arriving messages, stores the data in the SQL database.<br>
The AirQ-Runner works a little bit different. The AirQ provides data on a http-server. The runner requests that data every n seconds and stores it.
Runners inheret from the global runner class, that contains coder to unify the way, informations are passed trough the runners in the config.json and the interaction with the sql.

## Config.json and general Runner interface.

The config.json has multiple areals. One is the general field. General information on the sensor net, like address, port and database name of the database are contained here.
Per kind of runner that is used, a nother area has to be defined. The name of this area is runner specific. e.g. AirQ for the airQ-runners.
In this areal are different subsections. One per runner. The name of the runner section is the name of the table that will be used to store data from that runner. If there is an areal named AirQ1 in the AirQ areal, there will be an AirQ1 table in teh db. Further, the field must contain the information that is needet to access the rescouce. In the case of the shelly plug these infos are the name of the shelly plug to identify the MQTT topic.
The handling of these informations is automatically done by the runner.py parent class. The child classes just have to implement specific parts and get specific informations passed directly.


## Running the Sensor Network

## Different Runner instances

![](.figures/RunnerPolymorphism.png)

### AirQ Runner

### Shelly Plug Runner

## Setting up the Network.

This section contains a step by step guide to setup an instance of the sensornetwork containing one server and one or more AirQ Sciences and one or more Shelly-Plugs.
In this network, the server is running an mqtt server and a MariaDB instance. Both are configured to be accessible from all locations. Restrictions are coordinated by the firewall on the server,
which, in this guide is configured using ufw.<br>
In this configuration, IP-Addresses are assigned statically by the router.
In this Example, we use a raspberry pi 400 as server.
The guide contains the following sections:

* Step 1: Configuration of the Router
* Step 2: Installing an OS on the server
* Step 3: Installing and configuring ufw
* Step 4: Installing and testing MariaDB
* Step 5: Installing and testing MQTT
* Step 6: Integration and Configuration of the Shelly Plugs
* Step 7: Integration and Configuration of the Air Q Science.
* Step 8: Deploying the code in this repo.
* Step 9: Final steps. Making the configuration reboot save.
* Step 10 (Optional): Installing a graphic DB-Browser

This guide is for the following program versions:

| Software 	| Version 		|
|----------	|---------		|
| OS		| Raspbian (Linux 6.1.21-v8+ #1642 SMP PREEMPT Mon Apr  3 17:24:16 BST 2023 GNU/Linux) |
| ufw		| 0.36			|
| mariadb	| Ver 15.1 Distrib 10.5.21-MariaDB, for debian-linux-gnueabihf (armv7l) using  EditLine wrapper|
| mosquitto 	| 2.0.11		|
| python 	| 3.9.2			|
| python pip 	| 20.3.4		|
| pycryptodome	| 3.19.0		|
| paho-mqtt	| 1.6.1			|
| python mariadb| 1.0.11		|

### Step 1: Configuration of the Router
We don't go into the details of configuring the router since the configuration depends on the installed firmware. We assume that there is a documetntation from the manifacturer of the router.
For out Prototype we used a TP-Link WR841N Router.<br>
We configured the router to provide a hidden wifi network.
We also fixed the IP-Address for the computer, we use to administrate the network.

### Step 2: Installing an OS on the server
For the server we used the headless version of raspbian.

Here is a bit of confusion around the internet on how to configure this system.
In earlyer versions of raspbian you would have flased the system onto an sd-card and would have provided a file with the credentials of you network. Upon first boot,
the pi would than log into the network and you could login remotely via ssh as default user.<br>
This procedure changed. The network as well as the user for the ssh connection can be created with the rpimager tool by clicking on the "cog"-symbol before flasing.

Now is a good time to update the system:
After some time the machine should appear in the network. To establish an ssh connection use:

<pre><code>
ssh userName@ip.add.res.s
</code></pre>

On the machine 
<pre><code>
sudo apt-get update
sudo apt-get upgrade
</code></pre>
can be run to update the machine. If not done already, this is also a good moment to allocate the current ip-address as fixed address for the server in the router configuration.

### Step 3: Installing and configuring ufw

To controll the visibility and accessability of all services on the server, ufw will be installed.

<pre><code>
sudo apt-get install ufw
</code></pre>

In ufw, we go for a configuration, where every incomming connection is denied, instead of some connections that we explicitly allow.<br>
To add a rule that denies every incomming connection run:

<pre><code>
sudo ufw default deny incoming
</code></pre>

The next command allows us to connect to the machine via ssh (IMPORTANT):

<pre><code>
sudo ufw allow ipOfYourMachine on any port 22
</code></pre>

Here, ipOfYourMachine is the machine you want to use for the administration.
To allow a connection from Your machine to MariaDB (as soon as maria DB is installed) add the following rule:

<pre><code>
sudo ufw allow ipOfYourMachine on any port 3306
</code></pre>

(We use the default MariaDB port)
The rule for MQTT is a bit diffrent. Since we operate on a closed hidden network, we don't want to explicitly allow every device in the network to use the MQTT broker provided by our server. We just allow all incomming connections from the sub mask of our network to use the mqtt-broker:

<pre><code>
sudo ufw allow Sub.Net.Mask.Of.Rooter.0/24 to any port 1883
</code></pre>

To double check, if the rules are correct (especially the one for ssh) You can run:

<pre><code>
sudo ufw status
</code></pre>

To enable the fire wall, once everything is correct, run:

<pre><code>
sudo ufw enable
</code></pre>

### Step 4: Installing and testing MariaDB

Install mariadb on the server:

<pre><code>
sudo apt-get install mariadb-server
</code></pre>

At the moment mariadb is configured to only be availabel on the loopback interface of the machine.
To check, if the installation is working so far use:

<pre><code>
sudo mysql -u root
</code></pre>

to make the database accessible on the network, two things must be done: The database needs to be set up to be available on the local network, and a user with premissions to access the database from outside the local machine needs to be created.

To open the db-server on the local net edit the following file:

<pre><code>
/etc/mysql/mariadb.conf.d/50-server.cnf
</code></pre>

That file contains a line that reads:

<pre><code>
bind-address = 127.0.0.1
</code></pre>

This ties the database to the loopback interface. We changed the line to 

<pre><code>
bind-address = 0.0.0.0
</code></pre>

effectively opening the database on all network interfaces available from all ip-addresses. A binding to a subnet mask would have been more elegant, but I could not figure out how to do it. <br>
For changes in the config to take affect, You need to restart the mariaDB-server:

<pre><code>
systemctl restart mariadb.service
</code></pre>

To create a user that can access the database log in again with:

<pre><code>
sudo mysql -u root
</code></pre>

To create a user that can administrate all databases on the server use:

<pre><code>
CREATE USER name@ipOfYourMachine IDENTIFIED BY 'password';
GRANT ALL ON *.* TO name@ipOfYourMachine WITH GRANT OPTION;
</code></pre>

You also need to create the database that is later used to store the data from the sensor network.
<pre><code>
CREATE DATABASE SensorNetwork1;
</code></pre>


To test this newly established user on the other machine, You first need to install the mariadb-client on that machine:

<pre><code>
sudo apt-get install mariadb-client
</code></pre>

to log on with that client use:

<pre><code>
mysql --host=ipAddressOfTheDBServer -u nameOfTheUser --port 3306 -p
</code></pre>

The -p flag at the end indicates, that we log in with a password.
If everything worked out, you should see a mysql shell.

### Step 5: Installing and testing MQTT

In our version of the network, we use eclipse mosquitto, which is an open source mqtt broker.
To install the broker, log on to the server run:

<pre><code>
sudo apt-get install mosquitto mosquitto-clients
</code></pre>

The first package installs the broker, the second one installs some clients that can be used for testing the broker.
The default configuration for Mosquitto is, that it listens and broadcasts on the loopback interface without restrictions for the clients.
However, if we want to bind mosquitto to another networkinterface, we have to provide a policy to explicitly define the rights of the clients on that interface.<br>
Again, since we are managing who has access to what with the firewall anyway, we wanna create a policy that lets every client use the mqtt broker without authentification.<br>
To open the broker to the network, we edit the file
<pre><code>
/etc/mosquitto/mosquitto.conf
</code></pre>
and append the line

<pre><code>
Listener 1883
</code></pre>
. Now the broker is available on port 1883. In addition, to allow anyone on the network to access the broker, we edit 
<pre><code>
/etc/mosquitto/mosquitto.conf
</code></pre>
and include the line
<pre><code>
Allow\_anonymous true
</code></pre>
. For the new configurations to take affect, we need to restart the broker:
<pre><code>
systemctl restart mosquitto.service
</code></pre>

The configuration can be tested with the following two programms:
<pre><code>
mosquitto\_pub #can be used to post a message
musquitto\_sub #can be used to subscribe to a topic
</code></pre>

Hint:

If you want to find devices on the bus, wild cards are very handy. The # in mqtt lets you subscribe to all topics.

### Step 6: Integration and Configuration of the Shelly Plugs

The shelly plugs have to be configured to broadcast their status via mqtt.
To do so, plug in the shelly plug and wait, until the LED on the case turns green.
You should see an open WLAN that is hosted by the plug. Connect to that network and open a browser to connect to the gateway address (xxx.xxx.xxx.0).
In the networksetting of the webinterface enter the credentials of your wifi network to connect the shelly plug to the network.
When the plug is connected to the network, connect to the webinterface again and go to 'internet & security\>advanced settings' and enable mqtt by entering the servers ip address and port:
<pre><code>
ip.of.ser.ver:port
</code></pre>
You can test, if the connection to MQTT is succsessfull by using the mosquitto\_sub command.
Finally, navigate to 'settings\>device info' and note the device id. It will be important in the configuration of the code in this repository.
Repeat this procedure for all shelly plugs.

### Step 7: Integration and Configuration of the Air Q Science.

We configure the Air-Q stations to connect to the hidden network. The data will be sourced via the http connction.
To configure the Air-Q, we use the option to configure via sd-card. When a json file named config.json is placed on the sd card, the Air Q automatically restarts and applies this configuration. Data on the sd-card is formated during this process. Our configuration file has following content:
 
<pre><code>
{
 "devicename":"Name of the Air Q",
 "airqpass":"A password for the Air Q here (is used for decryption)",
 "RoomType":"office",
 "cloudUpload":false,
 "WiFissid":"Name of the hidden WIfi here",
 "WiFipass":"Your Wifi Passwd here",
 "WiFihidden":true,
 "cloudUpload":false
 }
</code></pre>

If everything goes well, the Air Q should appear in the network. This is one of the devices that should have a fixed ip address. Make sure to configure it in the router settings.
Note the password and the ip of the Air Q it will be relevant for the configuration of the code in this repository.

### Step 8: Deploying the code in this repo.

To get the code from this repo running on your server, you need to download it from github. You can either download it using another machine and transfer it with scp or you can clone it directly on the server using the git command, which needs to be installed on raspbian (sudo apt-get install git)

<pre><code>
git clone https://github.com/Arn-BAuA/SensorNetwork.git
</code></pre>

After the code is downloaded, we need to setup a virtual environment for the necessairy python libraries to live in. To install the libraries, we use pip.

<pre><code>
sudo apt-get install python3-venv #to create environments.
sudo apt-get install python3-pip #pip for managing packages.
</code></pre>

Create a Virtual environment using:

<pre><code>
python -m venv path/to/venv/nameOfVenv
</code></pre>

Use the newly created virtual environment using:

<pre><code>
source path/to/venv/nameOfVenv/bin/activate
</code></pre>

All of the packages that will be installed now are staying in the venv, so the global environment of the os on the server stays clean.
Install the following packages:

<pre><code>
pip install paho-mqtt 	 # lets python communicate with mqtt
pip install mariadb 	 # lets python interface with MariaDB
pip install pycryptodome # to encrypt the data from the Air Q
</code></pre>

Now all the nessecairy packages should be installed. We now need to create a configuration for the sensor network. You can either edit the supplied SensorNetworkConfig.json file directly or copy it to create your own version. Doesn't matter, the config file of interes has to be passed as a parameter anyway. In the config, add the credentials of the Air Qs and Shelly Plugs we noted earlyer along side the addresses of the mqtt and sql server:


<pre><code>
{
"General":{
	"SQLAddress":"192.168.0.101",
	"SQLPort":"3306",
	"SQLDBName":"SensorNetwork1",
	"SQLUser":"user",
	"SQLPassword":"passwd",
	"MQTTinUse":true,
	"MQTT_IP":"192.168.0.101",
	"MQTT_Port":1883,
	"LogFile":"SensorNetwork.log"
},
"AirQs":{
	"AirQ1":{
		"IP":"192.168.0.103",
		"PW":"password here"	
	}
},
"ShellyPlugs":{
	"ShellyPlug1":{
		"PlugName":"Shelly ID here",
		"IsShellyPlugS":false
	}
}
}
</code></pre>

You can choose the names of the Air Qs and Shellys here (in the example its AirQ1 and ShellyPlug1). The tables for the data from these sources in the database are named accordingly.
Now everything should be ready to start the network. Do so using:

<pre><code>
python Supervisor.py YourConfig.json >> ../processOut.txt & disown
</code></pre>

If everything goes well, the name of the process that was created should be echoed. The processOut.txt file should remain empty. It is just there for the case that the process crashes, so the output is not lost, since we disowned the process. Disowning it means, that you can exit the shell without causing the process to stop.<br>
To check, if everything is working, log in to mysql:

<pre><code>
mysql --host=ipAddressOfTheDBServer -u nameOfTheUser --port 3306 -p
</code></pre>

there, you can check the tables generated by the script. They should have the names, given in the json file, e.g. AirQ1 or ShellyPlug1 in the json example above.

<pre><code>
USE SensorNetwork1;
SELECT * FROM ShellyPlug1;
SELECT time,temperature,sound,co2,tvoc FROM AirQ1 ORDER BY time DESC LIMIT 20;
</code></pre>

If everything worked out, you should see entries that where created in the last seconds.

### Step 9: Final Steps, making the configuration reboot save.

### Step 10 (Optional): Installing a graphic DB-Browser

