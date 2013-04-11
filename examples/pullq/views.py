from server.views import View
from engine.datamodel import User
from data import Track
import datetime

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
        for cs in x.outgoing:
            changesetList.append( { "id": cs.changeset[0:12],
                                    "author": cs.author,
                                    "status": "",
                                    "time": cs.date,    # this gets converted to a float time by makeJSONable()
                                    "comment": cs.comment } )
        caseList = []
        return { "exceptions": excList,
                 "changesets": changesetList,
                 "cases": caseList }
