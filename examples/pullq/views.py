from server.views import View
from engine.datamodel import User
from data import Track
import datetime
from cStringIO import StringIO

class TrackView(View):
    subject = Track

    def buildPreFilter( self, parms ):
        f = { "active": True }
        if 'owner' in parms:
            u = User.objects.get( login=parms['owner'] )
            f["owner"] = u
        return f

    def buildPostPredicate( self, parms ):
        return lambda x: True

    def buildFullPredicate( self, parms ):
        if 'owner' in parms:
            uid = User.objects.get( login=parms['owner'] ).id
            return lambda x: x.active and (x.owner.id == uid)
        else:
            return lambda x: x.active

    def headlineform( self, k, b, x ):
        return { "project": x.inFolder.inProject.name,
                 "folder": x.inFolder.name,
                 "label": x.label,
                 "url": x.sourceRepo,
                 "owner": { "login": x.owner.login,
                            "fullname": x.owner.label } }
    def detailform( self, k, b, x ):
        x.reload()
        excList = [ { "severity": "?",
                      "summary": "What are you talking about?" } ]
        changesetList = []
        issues = set()
        for cs in x.outgoing:
            changesetList.append( { "id": cs.changeset[0:12],
                                    "author": cs.author,
                                    "status": "",
                                    "time": cs.date,    # this gets converted to a float time by makeJSONable()
                                    "markedupcomment": markupIssues( cs.comment, issues ),
                                    "comment": cs.comment } )
        return { "exceptions": excList,
                 "changesets": changesetList,
                 "issues": sorted( list( issues ) ) }

import re

ISSUE_PATTERN = re.compile( "issue\s+(\d+)" )

import cgi

def markupIssues( src, fill ):
    out = StringIO()
    posn = 0
    while True:
        m = ISSUE_PATTERN.search( src, posn )
        if m is None:
            # flush the rest, and then we're done
            out.write( cgi.escape( src[posn:] ) )
            return out.getvalue()
        # flush what came before
        out.write( cgi.escape( src[posn:m.start()] ) )
        # start the markup
        out.write( '<a class="issueref" href="#">' )
        # write the body
        out.write( cgi.escape( src[m.start():m.end()] ) )
        # finish the markup
        out.write( '</a>' )
        # and continue
        posn = m.end()
