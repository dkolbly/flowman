#! /usr/bin/env python

import tempfile
import os
import time
import sys
import re
from cStringIO import StringIO
import traceback

SHELL_META = re.compile( r"[$\\'`<>{}();|*?\[\]\"]" )

class JobFailed(Exception):
    pass

def shellquote( word ):
    if SHELL_META.search( word ):
        return "'" + word.replace( "'", "'\\''" ) + "'"
    else:
        return word

class Logger(object):
    def __init__( self, stdout=True ):
        self.__fd, self.__path = tempfile.mkstemp( ".job" )
        self.__f = os.fdopen( self.__fd, 'w' )
        if stdout:
            self.__tee = sys.stdout
        else:
            self.__tee = None
    def getvalue( self ):
        return open(self.__path).read()
    def __del__( self ):
        try:
            os.unlink( self.__path )
        except OSError:
            pass
    def detail( self, msg ):
        self.__log( 'D', msg )
    def shell( self, words ):
        self.__log( 'X', ' '.join( [shellquote(w) for w in words] ) )
    def note( self, msg ):
        self.__log( 'N', msg )
    def warn( self, msg ):
        self.__log( 'W', msg )
    def error( self, msg ):
        self.__log( 'E', msg )
    def exception( self ):
        f = StringIO()
        traceback.print_exc( 12, f )
        self.__log( 'E', f.getvalue() )
    def __log( self, sev, msg ):
        t = time.time()
        tstr = time.strftime( "%Y-%m-%d %H:%M:%S %Z",
                              time.localtime(t) )
        pre = "%.3f [%s] %s | " % (t, tstr, sev)
        out = []
        for i,line in enumerate( msg.split("\n") ):
            line = line.rstrip()
            if i > 0:
                pre = " " * len(pre)
                pass
            out.append( pre + line + "\n" )
            pass
        tee = self.__tee
        for l in out:
            self.__f.write( l )
            if tee is not None:
                tee.write( l )
        self.__f.flush()
