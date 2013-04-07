import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol
 
 
class WorkflowClientProtocol(WampClientProtocol):
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
 
   def onSessionOpen(self):
      self.prefix( "wf", "http://rscheme.org/workflow#" )
      
      d1 = self.call("wf:foo", 1, 2).addCallback(self.show)
 
      ## we want to shutdown the client exactly when all deferreds are finished
      DeferredList([d1]).addCallback(self.done)
 
 
if __name__ == '__main__':
   log.startLogging(sys.stdout)
   f = WampClientFactory("ws://localhost:2001", debugWamp = True)
   f.protocol = WorkflowClientProtocol
   connectWS(f)
   reactor.run()
