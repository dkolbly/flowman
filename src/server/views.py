from engine.datamodel import User
from server.dal import TM
from hashlib import sha1
from bson import BSON

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
        print "Notify %r of %r on %r" % (self, event, item)

    def __run( self ):
        result = {}
        for x in self.view.subject.objects( **self.prefilter ):
            if self.postPredicate(x):
                v = BSON.encode(x.to_mongo())
                result[ x.id ] = v
        return result

    def initialize( self ):
        self.selection = self.__run()

    def update( self ):
        """
        Return a create/update/delete (CRUD) spec for this watch
        """
        old = self.reported
        new = self.selection
        old_keys = set( old.keys() )
        new_keys = set( new.keys() )
        crud = {}
        def key(k):
            return "m%s" % k
        def entry(k,v):
            return (key(k),BSON.decode(v))
        for k in old_keys & new_keys:
            if old[k] != new[k]:
                crud.setdefault( 'updated', [] ).append( entry( k, new[k] ) )
        for k in old_keys - new_keys:
            crud.setdefault( 'deleted', [] ).append( key(k) )
        for k in new_keys - old_keys:
            crud.setdefault( 'created', [] ).append( entry( k, new[k] ) )
        self.reported = self.selection
        return crud

class View(object):
    def watch( self, predicate ):
        """
        Create a watch on a view
        """
        return Watch( self, predicate )

class UserView(View):
    subject = User

