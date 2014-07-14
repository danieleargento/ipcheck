#!/usr/bin/python

import httplib
import os.path
import sys
import smtplib
from os.path import expanduser

IPStoreFile = ".externalipaddress"
dropboxIPStoreFile = expanduser("~") + "/Dropbox/externalipaddress" #Leave empty if there is not Dropbox installed on the machine
oldIPAddress = ""
thisIPAddress = ""

# Mail variables
mailHost = "localhost"
mailPort = "25"
mailRcpt = ["mymailaddress@mydomain.com"]
mailFrom = "NoReply@localnet.net"

# Get IP address querying checkip.dyndns.org and parsing the output
def getIPAddress():
	url = "checkip.dyndns.org"
    	conn = httplib.HTTPConnection(url)
    	conn.request("GET","/")
    	response = conn.getresponse()

    # Check the return code, if not OK abort the script
	if not (response.status == 200):
		print "Checking IP through dyndns failed because: " + response.reason
		sys.exit(1)

	data = response.read()
	conn.close()
	startIPIndex = data.find("Current IP Address: ") + 20
	stopIPIndex = data.find("</body>")
	ipAddress = data[startIPIndex:stopIPIndex]
	return ipAddress
	
# Send mail with IP address to the contact in global variable
# TODO: eventually substitute this string variables with a template
def sendMail(ipAddress):
	mailFromText = "Python Check IP Script"
	mailSubject = "House Net: External IP changed"
	mailBody = "Hi, the external IP of your network is changed, the new one is: " + ipAddress

	message = """\
	From: %s
	To: %s
	Subject: %s
	
	%s
	""" % (mailFromText, ", ".join(mailRcpt), mailSubject, mailBody)
	
	try:
		server = smtplib.SMTP(mailHost,mailPort)
		server.sendmail(mailFrom, mailRcpt, message)
		server.quit()
	except:
		e = sys.exc_info()[0]
		print "Mail sending error because: %s" % e
	
# Store a copy of the IP address file in the Dropbox directory
def storeOnDropbox(ipAddress):
	f = open(dropboxIPStoreFile,"w")
	f.write(thisIPAddress)
	f.close()
	print "IP address stored on Dropbox"


thisIPAddress = getIPAddress()
print "Acquired IP Address: " + thisIPAddress

# Checking if an address is already stored in the file
if (os.path.isfile(IPStoreFile)):
	print "IP Address found on file"
	f = open(IPStoreFile)
	lines = f.readline()
	f.close()
	oldIPAddress = lines
	print "IP Address found: " + oldIPAddress

# If the IP address is changed from the one on file, write it on file and, eventually, on Dropbox
if not (thisIPAddress == oldIPAddress):
	print "IP Address is changed"
	# Writing IP Address on file
	f = open(IPStoreFile,"w")
	f.write(thisIPAddress)
	f.close()
	print "Send mail with IP " + thisIPAddress
	sendMail(thisIPAddress)
	if not (dropboxIPStoreFile == ""):
		storeOnDropbox(thisIPAddress)

