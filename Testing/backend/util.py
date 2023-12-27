import const
from math import exp
def sq_dist(a,b):
	return ((a[0]-b[0])**2 + (a[1]-b[1])**2)

def dist(a,b):
	return sq_dist(a,b)**0.5

def rssi_model(rssi):
	return exp((rssi-const.A)/const.B)

def get_position(device_mac):
	if device_mac in const.positions:
		return const.positions[device_mac][0]
	else:
		return const.ANCHORS['3C:71:BF:99:F9:E0']