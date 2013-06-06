DomainTracker
=============
_by Govind Raghunath_

Description
-----------

Domain Tracker is an application which keeps track of changing NS, MX, and A records over time given a list of domains.
This is a work in progress; new features are still in the process of being added.

Basic Usage
-----------

Start DomainTracker.py with the following usage:

    DomainTracker.py <Database filepath> <Time (seconds) between scans>

This will create the database file if it does not already exist, then will scan every target in the database in an infinite loop, waiting the given time between each set of scans.

Start DBInterface.py with the following usage:

    DomainTracker.py <Database filepath>

This tool will allow you to add and remove targets, as well as view the results of the tracker.
