"""
Contains code for MQTT subscriber thread
"""

import json
import paho.mqtt.client as paho

import const

def rssi_callback(client, userdata, message):
	m = str(message.payload.decode("utf-8")).rstrip('\n').replace('\'','\"')
	data = json.loads(m)

	# Extract SSID of Beacon sent to MQTT Broker
	Beacon_SSID = message.topic.split('/')[2] 
	# Extract SSID and RSSI of Station scanned by Beacon
	Station_SSID, rssi = data['SSID'], data['RSSI'] # We use IPv4, so we use SSID instead of MAC

	const.data_queue.put((Beacon_SSID, Station_SSID, rssi))

# def csi_callback(client, userdata, message):
# 	m = str(message.payload.decode("utf-8")).rstrip('\n').replace('\'','\"')
# 	data = json.loads(m)
# 	print(*data.items())

def on_connect(client, userdata, flags, rc):	
	rssi_topic = "/rssi/#"
	# rssi_topic, csi_topic = "/rssi/#", "/csi/#"
	client.subscribe(rssi_topic)
	# client.subscribe(csi_topic)

	client.message_callback_add(rssi_topic, rssi_callback)
	# client.message_callback_add(csi_topic, csi_callback)

def connect(broker_ip, broker_port):
	client= paho.Client("Localization listener") 
	client.on_connect = on_connect

	client.connect(broker_ip,broker_port)

	client.loop_forever()
