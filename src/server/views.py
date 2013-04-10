from engine.datamodel import User
from engine.loader import loadDefinition
from server.dal import TM
from hashlib import sha1
from bson import BSON
from bson.objectid import ObjectId
from copy import deepcopy
import datetime
import time


class Watch(object):
    def __init__( self, view, parms ):
        """
        Create a watch within a view.  The view is responsible for
        interpreting the parameters to provide the three kinds of
        filters.  This instance is responsible for paying attention to
        the datamodel class (i.e., by means of the TriggerManager in
        server.dal) and maintaining a stateful model of what the
        client session knows, and updating the client appropriately.
        """
        self.view = view
        self.parms = parms
        self.prefilter = view.buildPreFilter( parms )
        self.postPredicate = view.buildPostPredicate( parms )
        self.fullPredicate = view.buildFullPredicate( parms )
        self.selection = {}
        self.reported = {}
        self.dirty = True
        TM.watch( self.view.subject, self )
        pass

    def didDelete( self, x_id, x ):
        if self.dirty:
            return      # we're already dirty
        if x_id not in self.selection:
            # it wasn't in our selection, so it doesn't affect us
            return
        self.__markDirty()
        pass
        
    def didCreate( self, x_id, x ):
        if self.dirty:
            return      # we're already dirty
        if not self.fullPredicate( x ):
            # it doesn't match our predicate, so it doesn't affect us
            return
        self.__markDirty()
        pass

    def didUpdate( self, x_id, x ):
        if self.dirty:
            return      # we're already dirty
        # three cases to consider:
        #  (1) the object used to be in our selection set but
        #      isn't any longer
        #  (2) the object was, and still is, part of our selection
        #      set, but the data has changed
        #  (3) the object was not in our selection set before
        #      but is now
        if x_id in self.selection:
            # cases (1) and (2); note that in either subcase,
            # the watch is dirty
            self.__markDirty()
        else:
            if self.fullPredicate( x ):
                self.__markDirty()

    def __markDirty( self ):
        self.dirty = True
        # TODO: tickle the client side of WatchService, so that
        # our client can get a notification

    def __run( self ):
        result = {}
        for x in self.view.subject.objects( **self.prefilter ):
            if self.postPredicate(x):
                v = BSON.encode(x.to_mongo())
                result[ x.id ] = (v,x)
        return result

    def update( self ):
        """
        Return a create/update/delete (CRUD) spec for this watch
        """
        if self.dirty:
            self.selection = self.__run()
            self.dirty = False
        old = self.reported
        new = self.selection
        old_keys = set( old.keys() )
        new_keys = set( new.keys() )
        crud = {}
        #def key(k):
        #    return "m%s" % k
        #def entry(k,v):
        #    return (k,BSON.decode(v))
        for k in old_keys & new_keys:
            if old[k] != new[k]:
                h = self.view.headlineform( k, *new[k] )
                crud.setdefault( 'updated', {} )[k] = h
        for k in old_keys - new_keys:
            crud.setdefault( 'deleted', [] ).append( k )
        for k in new_keys - old_keys:
            h = self.view.headlineform( k, *new[k] )
            crud.setdefault( 'created', {} )[k] = h
        self.reported = self.selection
        #print "================ CRUD "
        crud = makeJSONable( crud )
        #print `crud`
        return crud

    def details( self, key ):
        if not key.startswith( "mongo-oid-" ):
            raise ValueError, "invalid details key %r" % key
        k = ObjectId( key[10:] )
        entry = self.reported[k]
        return self.view.detailform( k, *entry )

def makeJSONable( d ):
    def rec(x):
        #print "rec ==> %r %r" % (type(x),x,)
        if isinstance(x,list):
            return map(rec,x)
        elif isinstance(x,tuple):
            return tuple(map(rec,x))
        elif isinstance(x,dict):
            return dict( [(rec(k),rec(v)) for k, v in x.items()] )
        elif isinstance(x,ObjectId):
            return "mongo-oid-%s" % x
        elif isinstance(x,datetime.datetime):
            return (time.mktime( x.timetuple() ) * 1000) \
                + (x.microsecond / 1000);
        else:
            return x
    return rec( deepcopy(d) )
            

class View(object):
    def watch( self, parms ):
        """
        Create a watch on a view
        """
        return Watch( self, parms )
    def headlineform( self, k, b, x ):
        """Return the headline form (JSON) for a given object.
        The default implementation just returns all the top-level objects.
        
        There are three arguments, the object [mongo] id,
        the BSON representation, and the MongoEngine object
        """
        d = {}
        for k, v in BSON.decode( b ).items():
            if k[0] != '_':
                d[k] = v
        return d
    def detailform( self, k, b, x ):
        """Return the detail form (JSON) for a given object.
        The default implementation is the same as the headline form."""
        return self.headlineform( k, b, x )

class UserView(View):
    subject = User

class ViewMetaFactory(object):
    def __init__( self ):
        self.factoryCache = {}
    def getFactory( self, factoryName ):
        if factoryName in self.factoryCache:
            return self.factoryCache[factoryName]
        if factoryName == "UserView":
            c = UserView
        else:
            c = loadDefinition( factoryName )
        assert issubclass( c, View )
        self.factoryCache[factoryName] = c
        return c

    def __call__( self, ctx, factoryName, parms ):
        c = self.getFactory( factoryName )
        return c().watch( parms )

#from autobahn.wamp import WampClientFactory, WampClientProtocol
#from twisted.internet.defer import inlineCallbacks, returnValue
#from twisted.internet.task import deferLater
#from autobahn.websocket import connectWS

openView = ViewMetaFactory()
from autobahn.wamp import exportSub, exportPub

class WatchService(object):
    @exportSub( "watch/", True )
    def subscribe( self, topicUriPrefix, topicUriSuffix ):
        parts = topicUriSuffix.split('/')
        watchId = int(parts[0])
        print "client subscribing to [%d]" % watchId
        # DE-NIED!
        return False

    @exportPub( "watch", True )
    def publish( self, topicUriPrefix, topicUriSuffix, event ):
        print "client wants to publish %r %r : %r" % (topicUriPrefix,
                                                      topicUriSuffix,
                                                      event)
        # let it through
        return event
