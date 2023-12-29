# Indoor Localization + Navigation Project Using ESP32

## Setup

### Setup MQTT Broker server (for Windows):
1. install Mosquitto MQTT Broker on Windows
[https://mosquitto.org/download/](https://mosquitto.org/download/)
2. Adding Mosquitto to system path
3. run Mosquitto in the Windows cmd

```bash
cd mqtt_broker/
mosquitto -v -c <path to mosquitto.conf>
```

### Setup Backend Server for Preprocessing RSSI values (Windows):
1. `cd` into `Testing/mqtt_client_python`
2. setup virtual env for python code
```bash
pip install virtualenv
virtualenv .env
```
3. activate virtual environment and install dependencies:

```bash
source .env/Scripts/activate
pip install paho-mqtt plotly scipy
```
4. run backend server paho-mqtt
- parameters:
    + `-i`: Host IP of broker (required) 
        Suggested: This is the IPv4 Address of the device that host MQTT server
    + `-p`: Port (required)
        Suggested: 1883 (MQTT port)
    + `-x`: x coordinates of current beacon in map
    + `-y`: y coordinates of current beacon in map

```bash
python main.py -i 192.168.1.1 -p 1883
```

## Path Loss Model: Estimate distance from RSSI (REceived Signal Strength)

### Our chosen Path Loss Model

**One-Slope Model**: The simple yet effective model for estimating distance from RSSI.

### Caculate parameters for Path Loss model

We run paho-mqtt, a python-based mqtt server to act as a mqtt client, that subscribes to RSSI values that the beacon sends to MQTT broker.

The folder that stores the experiment results and code: `mqtt_client_python/`

Our experiment setup is as follow:

- We choose a floorplan to use as experiment site, write a simple map of the site, and measure the utilized dimensions. Since ESP32 can emits not-so-strong WiFi signals, we choose our classroom for a Proof-of-Concept demo.
- We place the ESP32 (3 or 4), acting as Stations (emit WiFi signals), at corners of the room. Record coordinates of all Stations relative to our predefined map.
- We use another ESP32, acting as Beacon (receive WiFi RSSI from Stations and send to MQTT broker), and plan to place it at various fixed points in the map, with measured coordinates of each fixed point related to map
- **During the experiment:** we place the Beacon at our predefined fixed points, and record the RSSI values, then export to csv files. Our recorded files are saved in `mqtt_client_python/rssi_collected` with the following structure:

```
beacon1/
    station1.csv
    station2.csv
    station3.csv

station1.csv:
<Distance>, <RSSI>
```