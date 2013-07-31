#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script created by Pranav Sharma (pranavsharma2504@gmail.com)
# Initial version created on 31st July 2013 : 08:00 IST
# Current Version: 0.11.0
# Version Date: 31-07-2013 08:00

# NOTE: Following are required to be installed on your
# system in order for this script to work as intended:
#
# python2.7-dev - sudo apt-get install python2.7-dev
# RPi.GPIO - sudo apt-get install python-rpi.gpio
# MySQLdb - install by entering in terminal: sudo apt-get install python-mysqldb

### USER EDITABLES
CONFIGFILE = "config"  # without extension
REFRESHTIME = 1  # seconds
GPIO_PINS = [12, 11, 13, 15, 16]
### USER EDITABLES END
import time
try:
        import RPi.GPIO as GPIO
except RuntimeError:
        print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run the script")
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

# Initialise flags
DEMO = 0
DEMO_DELAY = 1    # Seconds
RUN_SERVER = 0
END_SCRIPT = 0

switch_pin = []
switch_state = []
switch_enabled = []

# Function to check flags
def check_flags():
    db = MySQLdb.connect(host="localhost", user=dbcreds.username, passwd=dbcreds.password, db="autohomepi")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM `flags`")
    rows = int(cursor.rowcount)
    print ("Flags:")
    for i in range(0, rows):
        row = cursor.fetchone()
        if(row[0] == "run_server"):    # Check if server is to run
            RUN_SERVER = int(row[1])

        if(row[0] == "demo" and row[1] != 0):
            DEMO = row[1]
        if(row[0] == "demo_delay"):
            DEMO_DELAY = int(row[1]) / 100  # Database uses "seconds*100" scheme
        if(row[0] == "end_script"):
            END_SCRIPT = int(row[1])
        # Check and update other flags here as well (if any)
        print ("Flag ", row[0], ":", row[1])
    print ("----------------------")
    cursor.close()
    db.close()
# check_flags ends


def show_demo(demo_mode):
    if (demo_mode == 1):
        for switch in GPIO_PINS:
            GPIO.output(switch, 1)
            time.sleep(DEMO_DELAY)
        for switch in GPIO_PINS:
            GPIO.output(switch, 0)
            time.sleep(DEMO_DELAY)
    elif (demo_mode == 2):
        for switch in GPIO_PINS:
            GPIO.output(switch, 1)
            time.sleep(DEMO_DELAY)
        for switch in reversed(GPIO_PINS):
            GPIO.output(switch, 0)
            time.sleep(DEMO_DELAY)
    elif (demo_mode == 3):
        for switch in GPIO_PINS:
            GPIO.output(switch, 1)
            time.sleep(DEMO_DELAY)
        for i in range(0, len(GPIO_PINS)):
            GPIO.output(GPIO_PINS[i], 0)
            if(i != 0):
                GPIO.output(GPIO_PINS[i - 1], 1)
            time.sleep(DEMO_DELAY)
            GPIO.output(GPIO_PINS[i], 1)
        for i in range(len(GPIO_PINS), 0):
            GPIO.output(GPIO_PINS[i], 0)
            if (i != len(GPIO_PINS)):
                GPIO.output(GPIO_PINS[i + 1], 1)
            time.sleep(DEMO_DELAY)
            GPIO.output(GPIO_PINS[i], 1)
    elif (demo_mode == 99):            # Demo to show when ending demo
        for switch in GPIO_PINS:
            GPIO.output(switch, 1)
            time.sleep(DEMO_DELAY)
        for switch in reversed(GPIO_PINS):
            GPIO.output(switch, 0)
            time.sleep(DEMO_DELAY)

        for switch in GPIO_PINS:
            GPIO.output(switch, 1)
        time.sleep(DEMO_DELAY)
        for switch in GPIO_PINS:
            GPIO.output(switch, 0)
        time.sleep(DEMO_DELAY)
        for switch in GPIO_PINS:
            GPIO.output(switch, 1)
        time.sleep(DEMO_DELAY)
        for switch in GPIO_PINS:
            GPIO.output(switch, 0)
        time.sleep(DEMO_DELAY)
        for switch in GPIO_PINS:
            GPIO.output(switch, 1)
        time.sleep(DEMO_DELAY)
        for switch in GPIO_PINS:
            GPIO.output(switch, 0)
    for switch in GPIO_PINS:
        GPIO.output(switch, 0)
# show_demo(demo_mode) ends


def read_switches():
    db = MySQLdb.connect(host="localhost", user=dbcreds.username, passwd=dbcreds.password, db="autohomepi")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM `switches`")
    rows = int(cursor.rowcount)
    switch_pin = []
    switch_state = []
    switch_enabled = []
    print ("Reading pins: ")
    print ("\tSwitch\tPin\tValue\tStatus")
    for i in rows:
        row = cursor.fetchone()
        switch_pin.append(int(row[3]))
        switch_state.append(1 if(row[1] == "on") else 0)  # Active HIGH output
        switch_enabled.append(1 if(row[2] != "Disabled" or row[2] != "disabled") else 0)
        print (("\t", row[0], "\t", row[3], "\t", row[1], "\t", row[2]))
    print("-----------------")
    cursor.close()
    db.close()
    for i in rows:
        GPIO.setmode(switch_pin[i], GPIO.OUT if(switch_enabled[i]) else GPIO.IN)
        if(switch_enabled[i]):
            GPIO.output(switch_pin[i], switch_state[i])
# read_switches() ends

check_flags()


while (not END_SCRIPT):
    while(RUN_SERVER):
        # Running server
        while (DEMO):
            # Running in Demo mode
            for switch in GPIO_PINS:          # Set all used pins to output mode
                GPIO.setmode(switch, GPIO.OUT)
                GPIO.output(switch, 0)
            show_demo(DEMO)

            check_flags()
            if(not DEMO):
                show_demo(99)
                for switch in GPIO_PINS:
                    GPIO.setmode(switch, GPIO.IN)    # Disable all switches
            if(not RUN_SERVER):
                break
        read_switches()

        check_flags()
        if(not RUN_SERVER):
            # Ending while(RUN_SERVER). End tasks below
            for switch in GPIO_PINS:
                GPIO.output(switch, 0)
                GPIO.setmode(switch, GPIO.IN)        # Turn all used pins to input
        # while(RUN_SERVER) ends
    check_flags()
    # while(RUN_SERVER) ends

#db=MySQLdb.connect(host="localhost", user=dbcreds.username, passwd=dbcreds.password, db="autohomepi")
#cursor.close()
#db.close()
