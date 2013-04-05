from twisted.internet import reactor, protocol, threads
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import deferLater

from twisted.web.resource import Resource, NoResource, IResource, ForbiddenResource
from twisted.web.static import File
from twisted.web.server import Site
from autobahn.wamp import WampServerFactory, WampCraProtocol, WampCraServerProtocol, exportRpc, exportPub, exportSub
from autobahn.websocket import listenWS

from server.auth import AuthenticationManager
from server.notify import NotificationProtocol

AUTH_MGR = AuthenticationManager()

class NonBrowsableFile(File):
    def directoryListing( self ):
        return ForbiddenResource()

root = NonBrowsableFile( "src/www" )
root.putChild( "ext", NonBrowsableFile( ".run/www" ) )
root.putChild( "images", NonBrowsableFile( ".run/www/jquery.mobile-1.3.0/images" ) )

import time

class WorkflowProtocol(WampCraServerProtocol):

    def onConnect( self, c ):
        print "connection from %r" % (c.peer,)
        return WampCraServerProtocol.onConnect( self, c )

    @exportRpc
    def foo( self, x, y ):
        return [x,y,x]

    @exportRpc
    def getProjects( self ):
        return [ { "name": "p3",
                   "label": "Cayman" },
                 { "name": "p4",
                   "label": "Modules" } ]

    def anonPermissions( self ):
        return { "rpc": [ { 'uri': "http://rscheme.org/workflow#getProjects",
                            'call': True } ],
                 "pubsub": [ { 'uri': "http://rscheme.org/workflow#notification",
                               'prefix': True,
                               'pub': True,
                               'sub': True } ] }

    def userPermissions( self, user ):
        return { "rpc": [ { 'uri': "http://rscheme.org/workflow#getProjects",
                            'call': True } ],
                 "pubsub": [ { 'uri': "http://rscheme.org/workflow#notification",
                               'prefix': True,
                               'pub': True,
                               'sub': True } ] }

    def handleSubscription( self, base, suffix ):
        print "handleSubscription base=%r suffix=%r" % (base,suffix,)
        return True

    def onSessionOpen( self ):
        self.clientAuthTimeout = 0
        self.clientAuthAllowAnonymous = True
        self.registerForPubSub( "http://rscheme.org/workflow#", prefixMatch=True )
        WampCraServerProtocol.onSessionOpen( self )

    def getAuthPermissions( self, authKey, authExtra ):
        """Return permissions which we'll associate with
        the authentication key once auth succeeds; this will
        be the last arg to onAuthenticated(), and will also
        show up on the client.

        For our purposes, the authKey is the user login name."""
        def thunk():
            if authKey is None:
                # this is the anonymous path
                return { 'permissions': self.anonPermissions() }
            u = AUTH_MGR.getUser( authKey )
            if u is None:
                # this is the unknown user path
                print "No such user, %r" % (authKey,)
                return None
            else:
                rv = { 'permissions': self.userPermissions(u),
                       'authextra': AUTH_MGR.getAuthExtra(u) }
                return rv
        return threads.deferToThread( thunk )

    def getAuthSecret( self, authKey ):
        """Return the auth secret for the given key, or None
        if it is not known.   Note that we can return a deferred
        if we want to, in case the data is not immediately
        available."""
        thunk = lambda: AUTH_MGR.getAuthSecret( authKey )
        return threads.deferToThread( thunk )

    def onAuthenticated( self, authKey, perms ):
        self.registerForRpc( self, "http://rscheme.org/workflow#" )
        peer = self.peerstr
        if authKey is None:
            msg = "Anonymous connected from %s" % peer
        else:
            msg = "%s connected from %s" % (authKey,peer)
        deferLater( reactor, 1, lambda: NotificationProtocol.notify(msg) )



f = WampServerFactory( "ws://localhost:2001", debugWamp=True )
f.protocol = WorkflowProtocol
f.setProtocolOptions( allowHixie76=True )
listenWS(f)
NotificationProtocol.start()

from twisted.python import log

reactor.listenTCP( 2000, Site( root ) )
import sys
log.startLogging( sys.stdout )
log.msg( "starting" )

reactor.run()
