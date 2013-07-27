#!/usr/bin/python
# Script created by Pranav Sharma (pranavsharma2504@gmail.com)
# Initial version created on 27th July 2013 : 00:18 IST
# Current Version: 0.10.2
# Version Date: 27-07-2013 07:09

# NOTE: Following are required to be installed on your
# system in order for this script to work as intended:
#
# python2.7-dev - sudo apt-get install python2.7-dev
# RPi.GPIO - sudo apt-get install python-rpi.gpio
# MySQLdb - install by entering in terminal: sudo apt-get install python-mysqldb

### USER EDITABLES
CONFIGFILE = "config" #without extension
REFRESHTIME = 5 #seconds
### USER EDITABLES END
import time
try:
	import RPi.GPIO as GPIO
except RuntimeError:
	print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
GPIO.setmode(GPIO.BOARD)

try:
	dbcreds = __import__(CONFIGFILE, globals(), locals(), ['username', 'password'], -1)
except RuntimeError:
	print("Error importing config file. Please make sure a valid config file is present.")

try:
	import MySQLdb
except RuntimeError:
	print("Error importing python-mysqldb")
GPIO.setwarnings(False)
while 1:
	db = MySQLdb.connect(host="localhost", user=dbcreds.username, passwd=dbcreds.password, db="autohomepi")
	cursor = db.cursor()
	# execute SQL select query
	cursor.execute("SELECT * FROM `switches`")
	rows = int(cursor.rowcount)
	print "================================="
	print "|\tPin\tStatus\t\t|"
	for x in range(0,rows):
		row = cursor.fetchone()
		pin_no = int(row[3])
		if pin_no in [11, 12, 13, 15, 16]:
			pin_state = 0 if(row[1]=="on") else 1 #Inverting logic as we will be pulling uln2803 low to activate relay
			if(row[2]=="disabled" or row[2]=="Disabled"):
				GPIO.setup(pin_no, GPIO.IN)	# Set as input to avoid accidental short
				print "|\t",pin_no,"\tdisabled\t|"
			else:
				print "|\t",pin_no,"\t",pin_state,"\t\t|"
				GPIO.setup(pin_no, GPIO.OUT)
				GPIO.output(pin_no, pin_state)
		else:
			print "pin_no \'",pin_no, "\' not in valid range [11, 12, 13, 15, 16]"
	print "================================="
	cursor.close()
	db.close()
	time.sleep(REFRESHTIME)
