#! /usr/bin/env python

import data

class PullRequest(object):
    def __init__( self, folder ):
        self.inFolder = folder
    # this object defines the pull request workflow
    def create( self, className, parms ):
        # this is invoked by the createItem() dal API (server.dal.createItem)
        if className != 'Submission':
            raise TypeError, "we only create Submission objects"
        print "PullRequest create %r" % (parms,)

class Tracking(object):
    def __init__( self, folder ):
        self.inFolder = folder
    def create( self, className, parms ):
        if className != 'Track':
            raise TypeError, "we only create Track objects"
        # this is invoked by the createItem() dal API (server.dal.createItem)
        print "Track create: %r" % (parms,)
        url = parms['url']
        base = parms['base']
        return data.Track( sourceRepo=url,
                           baseRepo=base )
