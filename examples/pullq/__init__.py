#! /usr/bin/env python

"""
A development group workflow for pull requests.
The items are pull requests, and the states are phases
in the process some of which represent automatic processing
by other dev infrastructure.
"""

class Application(object):
    def start( self ):
        import pullq.services
        services.start()

