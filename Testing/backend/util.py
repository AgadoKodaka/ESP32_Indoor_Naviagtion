import const
from math import exp
def sq_dist(a,b):
	return ((a[0]-b[0])**2 + (a[1]-b[1])**2)

def dist(a,b):
	return sq_dist(a,b)**0.5

def rssi_model(rssi):
	return exp((rssi-const.A)/const.B)

def get_position(Beacon_SSID):
	if Beacon_SSID in const.positions:
		return const.positions[Beacon_SSID][0]
	else:
		raise Exception("Beacon not found in positions")