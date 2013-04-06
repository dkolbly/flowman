from engine.datamodel import User
import server.dal
from hashlib import sha1
from bson import BSON

class Watch(object):
    def __init__( self, view, predicate ):
        self.view = view
        self.prefilter = predicate.copy()
        if 'filter' in self.prefilter:
            self.postfilter = self.prefilter['filter']
            del self.prefilter['filter']
        else:
            self.postfilter = lambda x: True
        self.selection = {}
        self.reported = {}
        pass

    def __run( self ):
        result = {}
        for x in self.view.subject.objects( **self.prefilter ):
            if self.postfilter(x):
                v = BSON.encode(x.to_mongo())
                result[ x.id ] = v
        return result

    def initialize( self ):
        self.selection = self.__run()

    def collectionDidChange( self ):
        new = self.__run()
        if new != self.selection:
            print "watch changed"
            # signal a change

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

