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
* Step 9 (Optional): Installing a graphic DB-Browser

This guide is for the ver

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

### Step 6: Integration and Configuration of the Shelly Plugs

### Step 7: Integration and Configuration of the Air Q Science.

### Step 8: Deploying the code in this repo.

### Step 9 (Optional): Installing a graphic DB-Browser
