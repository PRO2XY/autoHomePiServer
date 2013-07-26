# Script created by Pranav Sharma (pranavsharma2504@gmail.com)
# Initial version created on 27th July 2013 : 00:18 IST
# Current Version: 0.10.1
# Version Date: 27-07-2013 03:14


### USER EDITABLES
CONFIGFILE = "config" #without extension
REFRESHTIME = 5 #seconds
### USER EDITABLES END
dbcreds = __import__(CONFIGFILE, globals(), locals(), ['DATABASEUSERNAME', 'DATABASEPASSWORD'], -1)
print (dbcreds.password)
