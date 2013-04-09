import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampCraClientProtocol
import threading

class RPCError(Exception):
    def __init__( self, errValue ):
        uri, desc, details = errValue
        self.__errValue = errValue
        print "================================================="
        print uri
        print desc
        for i in details:
            print i
        print "================================================="
        Exception.__init__( self, uri )

class AuthenticationError(Exception):
    def __init__( self, errValue ):
        uri, desc, details = errValue
        self.__errValue = errValue
        Exception.__init__( self, uri )

class WorkflowClientProtocol(WampCraClientProtocol):
   """
   An asynchronous client for talking to the workflow server
   """
 
   def show(self, result):
      print "SUCCESS:", result
 
   def logerror(self, e):
      erroruri, errodesc, errordetails = e.value.args
      print "ERROR: %s ('%s') - %s" % (erroruri, errodesc, errordetails)
 
   def done(self, *args):
      self.sendClose()
      reactor.stop()
 
   def onSessionOpen( self ):
       if self.factory.rpcAuth is None:
           d = self.authenticate()
       else:
           d = self.authenticate( authKey=self.factory.rpcAuth[0],
                                  authExtra=None,
                                  authSecret=self.factory.rpcAuth[1] )
       d.addCallbacks( self.onAuthSuccess, 
                       self.onAuthFailure )

   def onAuthFailure( self, err ):
       uri, desc, details = err.value.args
       #print "Authentication Error!", uri, desc, details
       self.factory.cnx.postResponse( 0, AuthenticationError(err.value.args) )
       
   def onAuthSuccess( self, perm ):
      self.prefix( "wf", "http://rscheme.org/workflow#" )
      self.factory.cnx.postResponse( 0, None )
      self.factory.cnx.session = self
      #d1 = self.call("wf:foo", 1, 2).addCallback(self.show)
 
      ## we want to shutdown the client exactly when all deferreds are finished
      #DeferredList([d1]).addCallback(self.done)

class Connection(object):
    def __init__( self, host, auth=None ):
        DEBUG = False
        f = WampClientFactory( "ws://%s:2001" % host, 
                               debugWamp = DEBUG)
        f.protocol = WorkflowClientProtocol
        f.rpcAuth = auth
        f.cnx = self
        self.session = None
        self.__factory = f
        self.nextRequestId = 1
        self.__pending = { 0: [None,threading.Event()] }
        self.__thread = threading.Thread( target=self.__run )
        self.__thread.daemon = True
        self.__thread.start()

    def __run( self ):
        connectWS( self.__factory )
        reactor.run( installSignalHandlers=0 )

    def postResponse( self, requestId, response ):
        p = self.__pending[requestId]
        p[0] = response
        p[1].set()

    def getResponse( self, requestId ):
        p = self.__pending[requestId]
        p[1].wait()
        del self.__pending[requestId]
        if isinstance( p[0], Exception ):
            raise p[0]
        return p[0]

    def ready( self ):
        x = self.getResponse(0)
    
    def __subscribe( self, cb, api ):
        self.session.subscribe( api, cb )

    def publish( self, api, event ):
        reactor.callFromThread( self.session.publish, api, event )

    def subscribe( self, api, cb ):
        """Subscribe to a pub/sub identifier; the callback (cb)
        is invoked with two arguments, the topicUri and the event,
        and *NOTE* is invoked from the reactor thread."""
        reactor.callFromThread( self.__subscribe, cb, api )

    def __invoke( self, requestId, api, args ):
        def cb(ret):
            self.postResponse( requestId, ret )
        def cberr(err):
            self.postResponse( requestId, RPCError( err.value.args ) )
        self.session.call(api, *args).addCallbacks( cb, cberr )
                              
    def rpc( self, api, *args ):
        requestId = self.nextRequestId
        self.nextRequestId += 1
        self.__pending[ requestId ] = [ None, threading.Event() ]
        reactor.callFromThread( self.__invoke,
                                requestId,
                                api,
                                args )
        return self.getResponse( requestId )

if __name__ == '__main__':
   log.startLogging(sys.stdout)
   Connection( "localhost", ('admin','admin') )
