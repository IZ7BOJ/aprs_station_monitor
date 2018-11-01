#!/usr/bin/env python

#******************************************************************************************
#This script periodically makes a query to aprs.fi database using APIs, and send a notification by telegram of the stations, or digipeater or igates that goes down/up.
#I used the script to monitor the vitality of a group o digipeaters, and to know the vitality situation in realtime.
#The vitality is assumed on the basis of the last packet registered on aprs.fi database coming from the stations to be monitored.
#If the last heard time is more than the timeout specified in the config section, the station is declared "dead"
#The telegram notifications are sent every time a station changes state (Alive to Dead and Dead to Alive)
#This script should be executed in background (sudo python aprs_stations_monitor.py &) and is configured to log errors and transition "alive->dead" and "dead->alive"

#IMPORTANT: before using this script, intall and configure the library "telegram-send ( https://pypi.org/project/telegram-send/ ) and configure the destination of the notifications (single user, group or channel)
#before using the script, every parameter of the config section must be declared.
#This script may have a lot of bugs, problems and it's written in very non-efficient way without a lot of good programming rules. But it works for me.
#Author: Alfredo IZ7BOJ iz7boj[--at--]gmail.com
#You can modify this program, but please give a credit to original author. Program is free for non-commercial use only.
#(C) Alfredo IZ7BOJ 2018

#Version 0.1beta
#*******************************************************************************************/

import httplib
import json
import sys
import time
from datetime import datetime
import logging
import numpy as np
import telegram_send

##############################################################################################
# CONFIGURATION SECTION
# DECLARE EVERY PARAMETER BEFORE USING THIS SCRIPT

apikey = '42447.qJOoyDfom0jANqXS' # insert your personal API key provided by aprs.fi (account required)
apiurl = 'api.aprs.fi' #aprs.fi api url. This should be changed only if notified by aprs.fi sysop
stations = 'IQ7NK-11,IW7EAP-11,IQ7YP,IZ7UNK-11,IK7EJT-10,IU7CMG-11,IR7T,IR7DD-11,IQ7GC-11' #insert stations to monitor, separated by comma
timeout = 5400 #timeout in seconds used to determine the station vitality
sleeptime = 30 #time in seconds between queries
maxattempts = 3 #maximum connection attempts to aprs.fi database before exit
logfile = '/var/log/aprsdash.log' #file to be written for the log (with the path)
telegram_conf_file = '/home/pi/.config/telegram-send.conf'
# END OF CONFIGURATION SECTION
############################################################################################

#start from "all stations active"
state_array = np.ones((len(stations.split(','))),dtype=int) #count the stations to be monitored and create the state array (all 1)

logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s') #initialize the log
logging.debug("daemon started")

try:  
	while True:	
		notconnected=1
		while (notconnected): #try to connect to aprs.fi api for "maxattempts" times
			try:
				conn = httplib.HTTPConnection(apiurl)
				conn.request('GET', '/api/get?name=' + stations + '&what=loc&apikey=' + apikey + '&format=json')
				notconnected=0
			except httplib.HTTPException:
				if i<maxattempts:
					print "Couldn't query aprs.fi! Let's try again.."
					logging.debug("Couldn't query aprs.fi! Let's try again..")
					i += 1
				else:
					print("Couldn't query aprs.fi! Maximum attempts reached. Exiting...")
					logging.debug("Couldn't query aprs.fi! Maximum attempts reached. Exiting...")
					sys.exit()	
		try:
			response = conn.getresponse() #get response
		except:
			print "Couldn't get a response from aprs.fi! Exiting..."
			logging.debug("Couldn't get a response from aprs.fi! Exiting..")
			conn.close()
			sys.exit()
		result   = response.read()
		
		try:
			jresult  = json.loads(result) #json parse the results
		except:
			print "Couldn't parse JSON from aprs.fi! Exiting..."
			logging.debug("Couldn't parse JSON from aprs.fi! Exiting...")
			conn.close()
			sys.exit()

		entries = jresult['entries']
		j=0
		for x in entries:
			name     = x['name'] #get callsign
			lasttime = x['lasttime'] #get last heard packet
			lasttime_utc=datetime.utcfromtimestamp(int(lasttime)).strftime('%Y-%m-%d %H:%M:%S') #convert from UTC unix time to human readable format
			if ((int(time.time()))-int(lasttime))>timeout:
				# Alive->Dead
				if state_array[j]==1:
					state_array[j]=0
					message = 'WARNING: Station ' + name + ' seems to be inactive from ' + str(lasttime_utc) +' GMT!'
					telegram_send.send(messages=[message], conf="/home/pi/.config/telegram-send.conf")
					logging.debug("Station " + name + " -->Dead")
			else:
				# Dead->Alive
				if state_array[j]==0:
					state_array[j]=1
					message = 'Station ' + name + ' is active again!'
					telegram_send.send(messages=[message], conf=telegram_conf_file)
					logging.debug("Station " + name + " -->Alive")
			j += 1
		conn.close()
		time.sleep(sleeptime) #wait "sleeptime" before next query


except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    conn.close()
    print("keyboard exception occurred")
    logging.debug("keyboard exception occurred")
    sys.exit()
