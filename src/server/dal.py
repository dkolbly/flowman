# Data Access Layer

from engine.datamodel import Project, Workflow, Folder, Item
from engine.datamodel import Attachment
from engine.datamodel import Audit, Comment, \
    Action, ManualAction, SpawnAction, ApprovalAction

class RestrictedView(object):

    def __init__( self, user, permissions ):
        self.user = user
        self.perm = permissions
        pass

    def getProjects( self ):
        lst = []
        for p in Project.objects():
            lst.append( { 'oid': assignoid(p),
                          'name': p.name,
                          'label': p.label,
                          'description': p.description } )
        return lst

def assignoid(x):
    return "x%d" % (hash(x) & 0xFFFFFFFF)
