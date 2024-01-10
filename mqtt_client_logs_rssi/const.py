from queue import Queue
from collections import OrderedDict

## Shared between MQTT listener and Data collector
data_queue = Queue()

## Stores positions of devices encountered so far
positions = OrderedDict()

## Coordinates of the Stations (APs)
STATIONS = {
	'Station1' : [0,280],
	'Station2' : [280,600],
	'Station3' : [600,280],
    'Station4': [280, 0]
}

## RSSI Model

TIME_WINDOW = 10

BEACON_NAME = 'beacon1'

