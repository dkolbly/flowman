from twisted.internet import reactor
from autobahn.wamp import WampClientFactory, WampClientProtocol
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import deferLater
from autobahn.websocket import connectWS
import time

class NotificationProtocol(WampClientProtocol):
    @classmethod
    def start( cls ):
        f = WampClientFactory( "ws://localhost:2001", debugWamp=True )
        f.protocol = NotificationProtocol
        connectWS(f)
        # uncomment this to produce a stream of debug notifications from
        # the server
        #deferLater( reactor, 1, lambda: cls.periodicDebugNotifier(0) )

    @classmethod
    def notify( cls, msg ):
        ev = [ int(1000*time.time()), msg ]
        for self in cls.NOTIFIERS:
            self.publish( self.uri, ev )

    NOTIFIERS = []

    def onSessionOpen( self ):
        print "Internal connection to notification service"
        #deferLater( reactor, 1, self.foo )
        self.uri = "http://rscheme.org/workflow#notification"
        self.NOTIFIERS.append( self )

    @classmethod
    def periodicDebugNotifier( cls, i ):
        cls.notify( "Test %d" % i )
        deferLater( reactor, 1, lambda: cls.periodicDebugNotifier(i+1) )
