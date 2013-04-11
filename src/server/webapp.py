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
from server.dal import createItem, InvocationContext
from server.views import openView, WatchService
from server.rest import setupREST

AUTH_MGR = AuthenticationManager()

class NonBrowsableFile(File):
    def directoryListing( self ):
        return ForbiddenResource()

root = NonBrowsableFile( "src/www" )
root.putChild( "ext", NonBrowsableFile( ".run/www" ) )
root.putChild( "app", NonBrowsableFile( ".run/app" ) )
root.putChild( "images", NonBrowsableFile( ".run/www/jquery.mobile-1.3.0/images" ) )
setupREST( root )


import time

class WorkflowProtocol(WampCraServerProtocol):

    def onConnect( self, c ):
        print "connection from %r" % (c.peer,)
        self.watches = {}
        self.nextWatchId = 100
        self.watchService = WatchService()
        self.registerHandlerForPubSub( self.watchService, 
                                       "http://rscheme.org/workflow#" )
        return WampCraServerProtocol.onConnect( self, c )

    @exportRpc
    def foo( self, x, y ):
        return [x,y,x]

    @exportRpc
    def setContext( self, projectName, roleName ):
        def thunk():
            self.context = InvocationContext( self.currentUser,
                                              projectName,
                                              roleName )
            return "ok"
        return threads.deferToThread( thunk )

    @exportRpc
    def refreshView( self, watchId ):
        w = self.watches[ watchId ]
        def thunk():
            x = w.update()
            x['id'] = watchId
            return x
        return threads.deferToThread( thunk )

    @exportRpc
    def getDetails( self, watchId, key, needTemplate ):
        watch = self.watches[ watchId ]
        def thunk():
            rsp = { 'id': watchId,
                    'details': watch.details(key) }
            if needTemplate:
                rsp['template'] = watch.view.detaildivtemplate()
            return rsp
        return threads.deferToThread( thunk )

    @exportRpc
    def openView( self, factoryName, parms ):
        watchId = self.nextWatchId
        self.nextWatchId += 1
        def thunk():
            w = openView( self.context, factoryName, parms )
            self.watches[ watchId ] = w
            x = w.update()
            x['id'] = watchId
            return x
        return threads.deferToThread( thunk )

    @exportRpc
    def createItem( self, className, inFolder, parms ):
        def thunk():
            return createItem( self.context, className, inFolder, parms )
        return threads.deferToThread( thunk )

    @exportRpc
    def getProjects( self ):
        return []
        #return threads.deferToThread( self.view.getProjects )

    def anonPermissions( self ):
        return { "rpc": [ { 'uri': "http://rscheme.org/workflow#",
                            'call': True } ],
                 "pubsub": [ { 'uri': "http://rscheme.org/workflow#notification",
                               'prefix': True,
                               'pub': True,
                               'sub': True } ],
                 "info": { "roles": [ { 'name': 'guest',
                                        'label': "Guest" } ] } }

    def userPermissions( self, user ):
        return { "rpc": [ { 'uri': "http://rscheme.org/workflow#",
                            'call': True } ],
                 "pubsub": [ { 'uri': "http://rscheme.org/workflow#notification",
                               'prefix': True,
                               'pub': True,
                               'sub': True } ],
                 "info": { "label": user.label,
                           "roles": [ { 'name': 'user',
                                        'label': "User" },
                                      { 'name': 'guest',
                                        'label': "Guest" },
                                      { 'name': 'operator',
                                        'label': "Operator" },
                                      { 'name': 'admin',
                                        'label': "Administrator" } ] } }

    def handleSubscription( self, base, suffix ):
        print "handleSubscription base=%r suffix=%r" % (base,suffix,)
        return True

    def onSessionOpen( self ):
        self.clientAuthTimeout = 0
        self.clientAuthAllowAnonymous = True
        self.registerForPubSub( "http://rscheme.org/workflow#", prefixMatch=True )
        self.registerForRpc( self, "http://rscheme.org/workflow#" )
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
        peer = self.peerstr
        if authKey is None:
            msg = "Anonymous connected from %s" % peer
        else:
            msg = "%s connected from %s" % (authKey,peer)
        self.currentUser = authKey
        self.currentRole = 'default'
        deferLater( reactor, 1, lambda: NotificationProtocol.notify(msg) )



f = WampServerFactory( "ws://localhost:2001", debugWamp=True )
f.protocol = WorkflowProtocol
#
# allowHixie76=True is required in order to work with iOS and Safari,
# but this is insecure
#
# see https://groups.google.com/forum/?fromgroups=#!topic/autobahnws/wOEU3Bvp4HQ

f.setProtocolOptions( allowHixie76=True )
listenWS(f)
NotificationProtocol.start()

from twisted.python import log

reactor.listenTCP( 2000, Site( root ) )
import sys
log.startLogging( sys.stdout )
log.msg( "starting" )

from application import MODULE
app = MODULE.Application()
app.start()

reactor.run()
