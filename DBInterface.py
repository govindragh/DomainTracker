import sys
import sqlite3

################################################################################
# HELPER FUNCTIONS
################################################################################

def printoptions():
    print 'Select one of the following options:'
    print '1.) List all targets.'
    print '2.) Add a new target.'
    print '3.) Delete a target.'
    print '4.) List all accumulated data for a target.'
    print '5.) Find all links to the target.'

def selectionprompt():
    inp = raw_input(' > ')
    try:
        ret = int(inp)
        return ret
    except ValueError:
        return -1

def listtargets(dbconn, dbcur):
    dbcur.execute('SELECT Target FROM Targets')
    targetrows = dbcur.fetchall()
    for targetrow in targetrows:
        print targetrow[0]

def addtarget(dbconn, dbcur):
    print '1.) Input the target manually.'
    print '2.) Import a text file of targets.'
    selection = selectionprompt()
    if selection == 1:
        newtarget = raw_input('Please enter the new target (enter nothing to cancel): ')
        if newtarget != '':
            dbcur.execute('INSERT INTO Targets (Target) VALUES (?)', (newtarget,))
            dbconn.commit()
    elif selection == 2:
        filepath = raw_input('Please enter the file path (enter nothing to cancel): ')
        if filepath != '':
            targetsfile = open(filepath, 'r')
            targetstext = targetsfile.read()
            targets = targetstext.split('\n')
            for newtarget in targets:
                dbcur.execute('INSERT INTO Targets (Target) VALUES (?)', (newtarget,))
                dbconn.commit()

def deltarget(dbconn, dbcur):
    deltarget = raw_input('Please enter the target to delete (enter nothing to cancel): ')
    if deltarget != '':
        dbcur.execute('DELETE FROM Targets WHERE Target = ?', (deltarget,))
        dbconn.commit()

def listdata(dbconn, dbcur):
    listtarget = raw_input('Please enter the target to list the data for (enter nothing to cancel): ')
    if listtarget != '':
        dbcur.execute('SELECT IPAddress, FirstDetected, LastDetected FROM Addresses WHERE DomainName = ?', (listtarget,))
        addressrows = dbcur.fetchall()
        print 'IP Address\tFirst Detected\tLast Detected'
        print '----------\t--------------\t-------------'
        for addressrow in addressrows:
            print str(addressrow[0]) + '\t' + str(addressrow[1]) + '\t' + str(addressrow[2])
        dbcur.execute('SELECT Addresses.DomainName, Type, MXPref, IPAddress, AssociatedServers.FirstDetected, AssociatedServers.LastDetected, Addresses.FirstDetected, Addresses.LastDetected FROM AssociatedServers, Addresses WHERE ParentDomain = ? AND AssociatedServers.DomainName = Addresses.DomainName ORDER BY Type, Addresses.DomainName', (listtarget,))
        addressrows = dbcur.fetchall()
        print 'Domain Name\tDomain Type\tIP Address\tAssociation First Detected\tAssociation Last Detected\tAddress First Detected\tAddress Last Detected'
        print '-----------\t-----------\t----------\t--------------------------\t-------------------------\t----------------------\t---------------------'
        for addressrow in addressrows:
            print str(addressrow[0]) + '\t' + str(addressrow[1]) + '\t' + str(addressrow[2]) + '\t' + str(addressrow[3]) + '\t' + str(addressrow[4]) + '\t' + str(addressrow[5]) + '\t' + str(addressrow[6])

def findlinks(dbconn, dbcur):
    print 'Not implemented yet.'

################################################################################
# MAIN
################################################################################

if len(sys.argv) != 2:
    print 'Usage: DomainTracker.py <Database filepath>'
    exit()

dbfilepath = sys.argv[1]

dbconn = sqlite3.connect(dbfilepath)
dbcur = dbconn.cursor()
while True:
    printoptions()
    selection = selectionprompt()
    print ''
    if selection == 1:
        listtargets(dbconn, dbcur)
    elif selection == 2:
        addtarget(dbconn, dbcur)
    elif selection == 3:
        deltarget(dbconn, dbcur)
    elif selection == 4:
        listdata(dbconn, dbcur)
    elif selection == 5:
        findlinks(dbconn, dbcur)
    else:
        print 'Please select a valid option!'
    print '================================================================================'
