#! /usr/bin/env python

class PullRequest(object):
    def __init__( self, folder ):
        self.inFolder = folder
    # this object defines the pull request workflow
    def create( self, parms ):
        # this is invoked by the createItem() dal API (server.dal.createItem)
        print "PullRequest create %r" % (parms,)

