import time
import argparse
import threading
import os

import const

from mqtt import *
from util import *

from scipy.optimize import minimize
from plot import plot_heatmap
import datetime

# Create folder for the beacon at the start
current_date = datetime.date.today()
beacon_folder_path = os.path.join('rssi_collected', const.BEACON_NAME, str(current_date))
if not os.path.exists(beacon_folder_path):
	os.makedirs(beacon_folder_path)

def data_listener(x, y):
	"""
	Listens to the queue filled up by MQTT listener

	Parameters:
		x, y: Coordinates of the current beacon
	"""
	while True:
		Beacon_SSID, Station_SSID, rssi = const.data_queue.get()

		# print(f"Beacon: {Beacon_SSID} - Station: {Station_SSID} - RSSI: {rssi}")

		distance = int(dist(const.STATIONS[Station_SSID], [x, y]))

		# Log the data immediately
		
		station_csv_path = os.path.join(beacon_folder_path, Station_SSID + '.csv')

		with open(station_csv_path, 'a') as f:
			f.write(f"{distance}, {rssi}\n")

		# Printing Summary of the RSSI values received
		print(f"Summary: {Station_SSID}-coor:{const.STATIONS[Station_SSID]} x:{x} y:{y} real_dist:{distance} {rssi}")


def data_listener_rssi_average(x,y):
	"""
	Listens to the queue filled up by MQTT listener

	Parameters:
		x, y: Coordinates of the current beacon
	"""
	rssi_data = {a: {} for a in const.STATIONS}

	while True:

		base_time = time.time()
		count = 0

		# Collecting RSSI values for TIME_WINDOW seconds
		while time.time() - base_time < const.TIME_WINDOW:
			Beacon_SSID, Station_SSID, rssi = const.data_queue.get()
			# print(Beacon_SSID, Station_SSID, rssi)
			count += 1
			
			if Beacon_SSID in rssi_data[Station_SSID]:
				rssi_data[Station_SSID][Beacon_SSID].append(rssi) 
			else:
				rssi_data[Station_SSID][Beacon_SSID] = [rssi]
		
		print("Received {} RSSI values in {} seconds".format(count, const.TIME_WINDOW))
		# Averaging the RSSI values collected in TIME_WINDOW seconds
		for Station_SSID in rssi_data:
			for Beacon_SSID in rssi_data[Station_SSID]:
				rssi_data[Station_SSID][Beacon_SSID] = round((1. * sum(rssi_data[Station_SSID][Beacon_SSID])) / len(rssi_data[Station_SSID][Beacon_SSID]),1)
				# Create paths for storing collected data
				# get current date
				current_date = datetime.date.today()
				beacon_path = os.path.join('rssi_collected', Beacon_SSID, current_date)
				station_csv_path = os.path.join(beacon_path, Station_SSID + '.csv')
				if not os.path.exists(beacon_path):
					os.mkdir(beacon_path)
				with open(station_csv_path, 'a') as f:
					f.write(f"{int(dist(const.STATIONS[Station_SSID], [x,y]))}, {rssi_data[Station_SSID][Beacon_SSID]}\n")

		## Printing Summary of the RSSI values received
		for Station_SSID in rssi_data:
			print(f"Summary: {Station_SSID}-coor:{const.STATIONS[Station_SSID]} x:{x} y:{y} real_dist:{int(dist(const.STATIONS[Station_SSID], [x,y]))} {rssi_data[Station_SSID]}")
		
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
	parser.add_argument("-i","--host", type=str, help="Host IP of broker", default="192.168.183.63")
	parser.add_argument("-p","--port", type=int, help="Port", default="1883")

	## Useful in building the path loss model
	parser.add_argument("-x", "--x", help="x coordinate of current beacon", type=int, default=560)
	parser.add_argument("-y", "--y", help="y coordinate of current beacon", type=int, default=300)
	# parser.add_argument("-b", "--beacon-name", help="Name of current beacon", type=str, default="beacon1")

	print("Starting paho-mqtt client to subscribe to RSSI data")

	args = parser.parse_args()
	print(args)


	mqtt_thread = threading.Thread(target=connect, args=(args.host, args.port))
	mqtt_thread.start()

	data_listener(x=args.x,y=args.y)
