from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.resource import Resource, NoResource, IResource, ForbiddenResource
from twisted.web.static import File
from twisted.web.server import Site
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc
from autobahn.websocket import listenWS

class NonBrowsableFile(File):
    def directoryListing( self ):
        return ForbiddenResource()

root = NonBrowsableFile( "../www" )
root.putChild( "ext", NonBrowsableFile( "../../.run/www" ) )
root.putChild( "images", NonBrowsableFile( "../../.run/www/jquery.mobile-1.3.0/images" ) )

class WorkflowProtocol(WampServerProtocol):
    @exportRpc
    def foo( self, x, y ):
        return [x,y,x]

    @exportRpc
    def getProjects( self ):
        return [ { "name": "p3",
                   "label": "Cayman" },
                 { "name": "p4",
                   "label": "Modules" } ]

    def onSessionOpen( self ):
        print "Got a session"
        self.registerForRpc( self, "http://rscheme.org/workflow#" )

f = WampServerFactory( "ws://localhost:2001" )
f.protocol = WorkflowProtocol
listenWS(f)
reactor.listenTCP( 2000, Site( root ) )
reactor.run()
