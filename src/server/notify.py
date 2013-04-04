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

    """
    @inlineCallbacks
    def foo( self ):
        for i in range(100):
            ev = [int(1000*time.time()),"Test %d" % i]
            self.publish( self.uri, ev )
            yield deferLater( reactor, 1, lambda: None )
          """
