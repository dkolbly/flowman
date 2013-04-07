#! /usr/bin/env python

import client.rpc
import argparse
import getpass

parser = argparse.ArgumentParser()
parser.add_argument( "--host", "-H" )
parser.add_argument( "--user", "-U" )
parser.add_argument( "--password", "-P" )
args = parser.parse_args()

def getAuthTuple( a ):
    if a.user or a.password:
        u = a.user or getpass.getuser()
        p = a.password or getpass.getpass( "Password for %s? " % u )
        return (u,p)
    return None

class NotificationTailer(object):
    def __init__( self, cnx ):
        cnx.subscribe( "wf:notification", self.notify )
    def notify( self, topic, event ):
        t = event[0] / 1000.0
        msg = event[1]
        notifyType = "-"
        notifyDetails = None
        if len(event) > 2:
            notifyType = event[2]
        if len(event) > 3:
            notifyDetails = event[3]
        print "%s.%03d %s %s" % (time.strftime( "%Y-%m-%d %H:%M:%S",
                                                time.localtime(t) ),
                                 event[0] % 1000,
                                 notifyType,
                                 msg)

cnx = client.rpc.Connection( (args.host or 'localhost'),
                             getAuthTuple(args) )
cnx.ready()
NotificationTailer( cnx )
print `cnx.rpc( 'wf:foo', 3, 4 )`
import time

time.sleep(60)

