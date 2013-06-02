import sys
import os
import sqlite3
import subprocess
import re
import datetime
import time

################################################################################
# HELPER FUNCTIONS
################################################################################

def initdb(dbfilepath):
    dbconn = sqlite3.connect(dbfilepath)
    dbcur = dbconn.cursor()
    dbcur.execute('CREATE TABLE Targets(Target TEXT)')
    dbcur.execute('CREATE TABLE AssociatedServers(ParentDomain TEXT, DomainName TEXT, Type TEXT, MXPref INT, FirstDetected TEXT, LastDetected TEXT)')
    dbcur.execute('CREATE TABLE Addresses(DomainName TEXT, IPAddress TEXT, FirstDetected TEXT, LastDetected TEXT)')
    dbconn.commit()
    dbconn.close()

def inetaddr(lineregex, dbcur):
    DomainName = lineregex.group(1)
    IPAddress = lineregex.group(3)
    dbcur.execute('SELECT * FROM Addresses WHERE DomainName = ? AND IPAddress = ?', (DomainName, IPAddress))
    existaddr = dbcur.fetchall()
    currtime = datetime.datetime.now()
    if len(existaddr) > 0:
        dbcur.execute('UPDATE Addresses SET LastDetected = ? WHERE DomainName = ? AND IPAddress = ?', (currtime, DomainName, IPAddress))
    else:
        dbcur.execute('INSERT INTO Addresses (DomainName, IPAddress, FirstDetected, LastDetected) VALUES (?, ?, ?, ?)', (DomainName, IPAddress, currtime, currtime))

def assocserv(lineregex, dbcur):
    ParentDomain = target
    if lineregex.group(2) == 'nameserver':
        Type = 'NameServer'
        MXPref = 0
    else:
        Type = 'MailExchanger'
        mxregex = re.search('MX preference = (\d*), mail exchanger', lineregex.group(2), re.DOTALL)
        MXPref = mxregex.group(1)
    DomainName = lineregex.group(3)
    dbcur.execute('SELECT * FROM AssociatedServers WHERE ParentDomain = ? AND Type = ? AND DomainName = ?', (ParentDomain, Type, DomainName))
    existassoc = dbcur.fetchall()
    currtime = datetime.datetime.now()
    if len(existassoc) > 0:
        dbcur.execute('UPDATE AssociatedServers SET LastDetected = ? WHERE ParentDomain = ? AND Type = ? AND DomainName = ?', (currtime, ParentDomain, Type, DomainName))
    else:
        dbcur.execute('INSERT INTO AssociatedServers (ParentDomain, DomainName, Type, MXPref, FirstDetected, LastDetected) VALUES (?, ?, ?, ?, ?, ?)', (ParentDomain, DomainName, Type, MXPref, currtime, currtime))

def processline(line, dbcur):
    lineregex = re.search('(.*?)\s*(internet address|nameserver|MX preference = \d*, mail exchanger) = (.*)\s', line, re.DOTALL)
    if lineregex != None:
        if lineregex.group(2) == 'internet address':
            inetaddr(lineregex, dbcur)
        else:
            assocserv(lineregex, dbcur)

################################################################################
# MAIN
################################################################################

if len(sys.argv) != 3:
    print 'Usage: DomainTracker.py <Database filepath> <Time (seconds) between scans>'
    exit()

dbfilepath = sys.argv[1]

try:
    waitinterval = int(sys.argv[2])
except ValueError:
    print 'The time between scans must be an integer.'

try:
    dbfile = open(dbfilepath, 'r')
    dbfile.close()
except IOError:
    dbfile = open(dbfilepath, 'w')
    dbfile.close()
    initdb(dbfilepath)

dbconn = sqlite3.connect(dbfilepath)
dbcur = dbconn.cursor()

while True:
    dbcur.execute('SELECT Target FROM Targets')
    targetrows = dbcur.fetchall()
    for targetrow in targetrows:
        target = targetrow[0]
        output = subprocess.check_output(['nslookup', '-query=all', target])
        outlines = output.split('\n')
        for line in outlines:
            processline(line, dbcur)
        dbconn.commit()
    time.sleep(waitinterval)
