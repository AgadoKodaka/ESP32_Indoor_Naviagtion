# Indoor Localization + Navigation Project Using ESP32

## Setup

### Setup MQTT Broker server (for Windows):
1. install Mosquitto MQTT Broker on Windows
[https://mosquitto.org/download/](https://mosquitto.org/download/)
2. Adding Mosquitto to system path
3. run Mosquitto in the Windows cmd

```bash
mosquitto -v -c <path to mosquitto.conf>
```

### Setup Backend Server for Preprocessing RSSI values (Windows):
1. `cd` into `Testing/backend`
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
        Suggested: 127.0.0.1 (localhost)
    + `-p`: Port (required)
        Suggested: 1883 (MQTT port)
    + `-x`: x coordinates
    + `-y`: y coordinates

```bash
python main.py -i 127.0.0.1 -p 1883
```
