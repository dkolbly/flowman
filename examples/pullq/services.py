#! /usr/bin/env python

import threading
import pullq.mercurial
import pullq.data 
import datetime
import time
from engine.job import Logger

class MercurialRepoMgr( object ):
    def run( self ):
        while True:
            l = Logger( stdout=False )
            show_output = False
            try:
                n = self.poll( l )
                if n > 0:
                    show_output = True
            except Exception as exc:
                l.exception()
                output = True
            if show_output:
                print l.getvalue()
            del l
            time.sleep(30)
    def poll( self, log ):
        inven = self.inventory()
        bases = set()
        total_new = 0
        for t in inven:
            bases.add( t.baseRepo )
        for u in bases:
            log.note( "updating %s" % (u,) )
            pullq.mercurial.hg_update( log, u )
        for t in inven:
            log.note( "checking %s" % (t.sourceRepo,) )
            total_new += self.poll1( log, t )
        return total_new
    def poll1( self, log, track ):
        lst = pullq.mercurial.hg_incoming( log,
                                           track.baseRepo, 
                                           track.sourceRepo )
        log.note( "  %d changes" % len(lst) )
        if len(lst) == 0:
            return 0
        pullq.mercurial.hg_pullin( log,
                                   track.baseRepo,
                                   track.sourceRepo,
                                   [cs['node'] for cs in lst] )
        lst = pullq.mercurial.hg_log( log,
                                      track.baseRepo,
                                      [cs['node'] for cs in lst] )
        num_new_cs = 0
        for i, cs in enumerate(lst):
            log.note( "  %3d: %s" % (i, cs['commentlines'][0] ) )
            t = datetime.datetime.fromtimestamp( cs['date'] )
            d = pullq.data.Changeset.objects( changeset=cs['node'] )
            if len(d) > 0:
                continue
            d = pullq.data.Changeset( changeset=cs['node'],
                                      date=t,
                                      author=cs['author'],
                                      comment='\n'.join( cs['commentlines'] ),
                                      createdFiles=cs['createdfiles'],
                                      deletedFiles=cs['deletedfiles'],
                                      modifiedFiles=cs['modifiedfiles'] )
            num_new_cs += 1
            if len( cs['parents'] ) > 0:
                p = self.__findcs( log, cs['parents'][0] )
                if p is not None:
                    d.parent1 = p
            if len( cs['parents'] ) > 1:
                p = self.__findcs( log, cs['parents'][1] )
                if p is not None:
                    d.parent2 = p
            d.save()
        return num_new_cs
    def __findcs( self, log, cs ):
        p = pullq.data.Changeset.objects( changeset=cs )
        if len(p) > 0:
            return p[0]
        else:
            log.warn( "No existing changeset %s" % cs )
                                  
    def inventory( self ):
        return pullq.data.Track.objects( active=True )

def start():
    t = threading.Thread( target=MercurialRepoMgr().run )
    t.daemon = True
    t.start()

                          
