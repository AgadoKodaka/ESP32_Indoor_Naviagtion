import time
import argparse
import threading

import const

from mqtt import *
from util import *

from scipy.optimize import minimize
from plot import plot_heatmap

	
def data_listener(x,y):
	"""
	Listens to the queue filled up by MQTT listener
	"""
	rssi_data = {a: {} for a in const.STATIONS}

	while True:

		base_time = time.time()

		while time.time() - base_time < const.TIME_WINDOW:
			Beacon_SSID, Station_SSID, rssi = const.data_queue.get()
			
			if Beacon_SSID in rssi_data[Station_SSID]:
				rssi_data[Station_SSID][Beacon_SSID].append(rssi) 
			else:
				rssi_data[Station_SSID][Beacon_SSID] = [rssi]

		for a in rssi_data:
			for d in rssi_data[a]:
				rssi_data[a][d] = round((1. * sum(rssi_data[a][d])) / len(rssi_data[a][d]),1)

		## Printing Summary of the RSSI values received
		for Station_SSID in rssi_data:
			print("Summary: ", Station_SSID,int(dist(const.STATIONS[Station_SSID], [x,y])), rssi_data[Station_SSID])
		
		# localize(rssi_data)
		rssi_data = {a: {} for a in const.STATIONS}
		# print_positions()

def print_positions():
	"""
	Prints positions of the devices encountered so far
	"""	
	pos = []
	for device_mac in const.positions:
		print(device_mac, *const.positions[device_mac][0], const.positions[device_mac][1])
		pos.append([dist(const.positions[device_mac][0], const.STATIONS[a])for a in const.STATIONS])
	plot_heatmap(pos)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--host", type=str, help="Host IP of broker", required=True)
	parser.add_argument("-p","--port", type=int, help="Port", required=True)

	## Useful in building the path loss model
	parser.add_argument("-x", "--x", help="x coordinate of current beacon", type=int, default=560)
	parser.add_argument("-y", "--y", help="y coordinate of current beacon", type=int, default=300)

	print("Starting paho-mqtt client to subscribe to RSSI data")

	args = parser.parse_args()

	print(args)

	mqtt_thread = threading.Thread(target=connect, args=(args.host, args.port))
	mqtt_thread.start()

	data_listener(x=args.x,y=args.y)
