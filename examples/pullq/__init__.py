#! /usr/bin/env python

"""
A development group workflow for pull requests.
The items are pull requests, and the states are phases
in the process some of which represent automatic processing
by other dev infrastructure.
"""

import threading

class Application(object):
    def start( self ):
        print "starting PULLQ application"
        import pullq.services
        hg = pullq.services.MercurialRepoMgr()
        t = threading.Thread( target=hg.run )
        t.daemon = True
        t.start()
