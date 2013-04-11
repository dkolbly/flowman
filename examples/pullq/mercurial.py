#! /usr/bin/env python

import hashlib
import os.path
import subprocess
from engine.job import JobFailed
import re


class LocalRepo(object):
    def __init__( self, top ):
        self.top = top
        self.toc = {}
        self.tocfile = os.path.join( self.top, "index.toc" )
        for l in open( self.tocfile ):
            x = l.strip().split('|',1)
            if len(x) == 2:
                self.toc[ x[1] ] = x[0]
    def temp( self ):
        i = 1
        while os.path.exists( os.path.join( self.top, "tmp%d" % i ) ):
            i += 1
        return os.path.join( self.top, "tmp%d" % i )
    def localFor( self, url ):
        if url in self.toc:
            return os.path.join( self.top, self.toc[url] )
        h = hashlib.sha1( url ).hexdigest()[0:16]
        f = open( self.tocfile, "a" )
        f.write( "%s|%s\n" % (h, url) )
        self.toc[ url ] = h
        d = os.path.join( self.top, h )
        return d

LOCAL = LocalRepo( "/tmp/PullQueue" )

class ProcessFailed(Exception):
    def __init__( self, msg, stdout, stderr, rc ):
        Exception.__init__( self, msg )
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = rc
    pass

def runshell( log, cmd ):
    log.shell( cmd )
    p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    (stdout, stderr) = p.communicate()
    p.wait()
    if p.returncode != 0:
        log.error( "error exit code %d" % p.returncode )
        raise ProcessFailed( "%s failed" % cmd[0], 
                             stdout,
                             stderr,
                             p.returncode )
    else:
        log.detail( "successful exit code" )
    return stdout

CHANGESET = re.compile( r"^changeset:\s*\d+:([0-9a-f]{40})" )

def parseMergeChangeLogNodes( stdout ):
    """'merge --preview' does not allow us to specify a template,
    so the output format is different :-(
    
    All we do, however, is return the list of nodes so we can
    match it up later with what we get from parsing the log
    """
    result = []
    for l in stdout.split('\n'):
        m = CHANGESET.match( l )
        if m:
            result.append( m.group(1) )
    return result
        
    

def parseChangeLog( stdout ):
    result = []
    info = None
    for l in stdout.split('\n'):
        if l.startswith( "ITEM|" ):
            if info:
                result.append( info )
            cols = l.split('|')
            afiles = set(cols[6].split())
            cfiles = set(cols[7].split())
            dfiles = set(cols[8].split())
            info = { "node": cols[1],
                     "rev": int(cols[2]),
                     "parents": [c.split(':')[1] for c in cols[3].split()
                                 if c != "-1:0000000000000000000000000000000000000000"],
                     "author": cols[4],
                     "date": float(cols[5]),
                     "commentlines": [],
                     "createdfiles": list(cfiles),
                     "deletedfiles": list(dfiles),
                     "modifiedfiles": list(afiles-(cfiles|dfiles)) }
        elif l.startswith( "\t" ):
            info['commentlines'].append( l[1:] )
    if info:
        result.append( info )
    return result
    
def hg_log( log, base_url, revs ):
    p = LOCAL.localFor( base_url )
    cmd = ["hg", "-R", p, 
           "--debug",
           "log", 
           "--template", "ITEM|{node}|{rev}|{parents}|{author}|{date}|{files}|{file_adds}|{file_dels}\\n\\t{desc|tabindent}\\n"]
    for i in revs:
        cmd.append( "-r%s" % i )
    stdout = runshell( log, cmd )
    return parseChangeLog( stdout )


def hg_identify( log, url ):
    cmd = ["hg", "--debug", "identify", url]
    x = runshell( log, cmd )
    lastline = x.split('\n')[-2]
    if re.match( r"^[0-9a-f]{40}$", lastline ):
        return lastline
    raise RuntimeError, "Unexpected output from hg identify"

def hg_update( log, base_url, rev ):
    p = LOCAL.localFor( base_url )
    cmd = ["hg", "-R", p,
           "update",
           "--clean",
           "--rev", rev]
    runshell( log, cmd )

def hg_merge_preview( log, base_url, rev ):
    p = LOCAL.localFor( base_url )
    cmd = ["hg", "-R", p,
           "--debug", "merge",
           "--preview",
           "--rev", rev]
    return runshell( log, cmd )


def hg_incoming( log, base_url, src_url ):
    p = LOCAL.localFor( base_url )
    log.detail( "repo %s" % p )
    cmd = ["hg", "-R", p, 
           "--debug",
           "incoming", 
           "--template", "ITEM|{node}|{rev}|{parents}|{author}|{date}|{files}|{file_adds}|{file_dels}\\n\\t{desc|tabindent}\\n",
           src_url]
    try:
        x = runshell( log, cmd )
    except ProcessFailed as exc:
        if (exc.returncode == 1) \
                and (exc.stderr == "") \
                and exc.stdout.endswith( "all remote heads known locally\nno changes found\n"):
            log.note( "(exit code 1 ==> 'all remote heads known')" )
            return []
        raise
    return parseChangeLog( x )

def hg_pullin( log, base_url, src_url, revs ):
    p = LOCAL.localFor( base_url )
    log.detail( "repo %s" % p )
    cmd = ["hg", "-R", p, "pull"]
    for i in revs:
        cmd.append( "-r%s" % i )
    cmd.append( src_url )
    runshell( log, cmd )

def hg_pull( log, src_url ):
    p = LOCAL.localFor( src_url )
    log.detail( "repo %s" % p )
    if os.path.exists( p ):
        cmd = ["hg", "-R", p, "pull", src_url]
    else:
        cmd = ["hg", "clone", "--noupdate", src_url, p]
    runshell( log, cmd )

def hg_merge( log, src_url, dst_url, cs, comment, branch="default" ):
    s = LOCAL.localFor( src_url )
    d = LOCAL.localFor( dst_url )
    t = LOCAL.temp()
    runshell( log, ["hg", "clone", d, t] )
    runshell( log, ["hg", "-R", t, "pull", "-r", cs, s] )
    stdout = runshell( log, ["hg", "-R", t, "heads", 
                             "--template", "{branches}|{node}\\n" ] )
    heads = {}
    for x in stdout.split("\n"):
        if '|' in x:
            (branchName,revNum) = x.split('|')
            if branchName == "":
                branchName = "default"
            heads.setdefault( branchName, [] ).append( revNum )
            pass
        pass
    if branch not in heads:
        log.error( "No heads of branch %r" % (branch,) )
        raise JobFailed
    if len(heads[branchName]) == 1:
        log.note( "Clean stack... no merge required" )
        return None
    #======================================================================
    log.note( "merging %d heads of branch %s" % (len(heads[branch]),
                                                 branch) )
    cmd = ["hg","-R", t, "-y","merge","-t","false"]
    try:
        runshell( log, cmd )
    except ProcessFailed as ex:
        raise JobFailed("merge failed")
    #======================================================================
    cmd = ["hg","-R",t, "resolve", "-l"]
    stdout = runshell( log, cmd )
    anyUnresolved = False
    conflicts = []
    for l in stdout.split("\n"):
        if not l:
            continue
        if l[0] != 'R':
            anyUnresolved = True
            conflicts.append( l[2:].strip() )
    if anyUnresolved:
        log.error( "Merge conflicts:\n%s" % ('\n'.join(conflicts),) )
        raise JobFailed( "merge conflicts" )
    #======================================================================
    cmd = ["hg", "-R", t, "commit", "-m", comment]
    runshell( log, cmd )
    #======================================================================
    bundlePath = os.path.join( t, "merge.bundle" )
    cmd = ["hg", "-R", t, "bundle", bundlePath, d]
    runshell( log, cmd )
    return bundlePath
