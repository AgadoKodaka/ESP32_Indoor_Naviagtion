from queue import Queue
from collections import OrderedDict

## Shared between MQTT listener and Data collector
data_queue = Queue()

## Stores positions of devices encountered so far
positions = OrderedDict()

## Coordinates of the Stations (APs)
STATIONS = {
	'Station1' : [0,0],
	'Station2' : [600,0],
	'Station3' : [360,600]
}

## RSSI Model

TIME_WINDOW = 10

BEACON_NAME = 'beacon1'

