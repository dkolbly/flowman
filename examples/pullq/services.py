#! /usr/bin/env python

import pullq.mercurial
import pullq.data 
import datetime
import time
from engine.job import Logger

class MercurialRepoMgr( object ):
    def run( self ):
        while True:
            l = Logger()
            #l = Logger( stdout=False )
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
        bases = {}
        total_new = 0
        # organize all the tracks by their baseRepo URL
        for t in inven:
            bases.setdefault( t.baseRepo, [] ).append(t)
        # update the base repositories
        dirty = set()
        for url, tracks in bases.items():
            log.note( "refreshing base repo %s" % url )
            self.refresh_base( log, url, tracks, dirty )
        # for each track in our inventory, update the info in it
        for t in inven:
            log.note( "refreshing track %r" % t )
            n, changed = self.refresh_info( log, t )
            if changed:
                dirty.add( t )
            print "XX t => %r" % (t,)
            print "XX t.tip => %r" % (t.tip,)
            total_new += n
        # recheck merges for everything that has changed
        for t in dirty:
            log.note( "checking merge for %r" % t )
            print "YY t => %r" % (t,)
            print "YY t.tip => %r" % (t.tip,)
            self.refresh_merge( log, t )
        return total_new

    def refresh_merge( self, log, t ):
        print "RM t => %r" % (t,)
        print "RM t.tip => %r" % (t.tip,)
        x = pullq.mercurial.hg_merge_preview( log, 
                                              t.baseRepo, 
                                              t.tip.changeset )
        nodes = pullq.mercurial.parseMergeChangeLogNodes( x )
        lst = pullq.mercurial.hg_log( log, t.baseRepo, nodes )
        n, csl = self.load_changesets( log, lst )
        t.outgoing = csl
        t.save()
        
    def refresh_base( self, log, url, tracks, dirtyTracks ):
        log.note( "updating %d tracks using %s" % (len(tracks),url,) )
        pullq.mercurial.hg_pull( log, url )
        basisNode = pullq.mercurial.hg_identify( log, url )
        basis = self.ensure_changeset( log, url, basisNode )
        # update the working directory to the externally mentioned "tip"
        pullq.mercurial.hg_update( log, url, basisNode )
        # update the basis pointer
        for t in tracks:
            if t.basis != basis:
                log.note( "updated track %r basis to %r" % (t, basis) )
                t.basis = basis
                dirtyTracks.add( t )
                t.save()
    def refresh_info( self, log, track ):
        tipNode = pullq.mercurial.hg_identify( log, track.sourceRepo )
        lst = pullq.mercurial.hg_incoming( log,
                                           track.baseRepo, 
                                           track.sourceRepo )
        log.note( "%r has %d incoming" % (track,len(lst)) )
        if (len(lst) == 0) and track.tip and (track.tip.changeset == tipNode):
            return 0, False
        pullq.mercurial.hg_pullin( log,
                                   track.baseRepo,
                                   track.sourceRepo,
                                   [tipNode] )
        if len(lst) > 0:
            lst = pullq.mercurial.hg_log( log,
                                          track.baseRepo,
                                          [cs['node'] for cs in lst] )
            num_new, csl = self.load_changesets( log, lst )
        else:
            num_new = 0
            csl = []
        # update the 'tip' and 'basis' Changeset pointers
        tip = self.ensure_changeset( log, track.baseRepo, tipNode )
        log.note( "  updating tip to %r" % tip )
        track.tip = tip
        log.note( "  tip => %r" % (track.tip,) )
        track.outgoing = csl
        track.save()
        log.note( "  tip => %r after save" % (track.tip,) )
        return num_new, True

    def ensure_changeset( self, log, baseRepo, node ):
        """Try to make sure a Changeset() object exists; if it
        doesn't already, pull the log entry and create it"""
        d = pullq.data.Changeset.objects( changeset=node )
        if len(d) > 0:
            return d[0]
        logEntry = pullq.mercurial.hg_log( log, baseRepo, [node] )
        if len(logEntry) != 1:
            raise RuntimeError, "invalid data from hg_log(), %d" % len(logEntry)
        if logEntry[0]['node'] != node:
            raise RuntimeError, "invalid entry from hg_log(), expected %r got %r" % (node, logEntry[0]['node'])
        self.load_changesets( log, logEntry )
        d = pullq.data.Changeset.objects( changeset=node )
        assert( len(d) == 1 )
        return d[0]

    def load_changesets( self, log, lst ):
        num_new_cs = 0
        csl = []
        for i, cs in enumerate(lst):
            log.note( "  %3d: %s" % (i, cs['commentlines'][0] ) )
            t = datetime.datetime.fromtimestamp( cs['date'] )
            d = pullq.data.Changeset.objects( changeset=cs['node'] )
            if len(d) > 0:
                csl.append( d[0] )
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
            csl.append( d )
        return (num_new_cs, csl)
    def __findcs( self, log, cs ):
        p = pullq.data.Changeset.objects( changeset=cs )
        if len(p) > 0:
            return p[0]
        else:
            log.warn( "No existing changeset %s" % cs )
                                  
    def inventory( self ):
        return pullq.data.Track.objects( active=True )
