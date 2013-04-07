from twisted.web.resource import Resource
from server.dal import Project
import json

class ItemResource(Resource):
    def __init__( self, projectName, folderName, itemName ):
        Resource.__init__( self )
        self.projectName = projectName
        self.folderName = folderName
        self.itemName = itemName
    def render_GET( self, request ):
        return json.dumps( { "_type": "Item",
                             "name": self.folderName,
                             "inFolder": self.folderName,
                             "inProject": self.projectName } )
        
class FolderResource(Resource):
    def __init__( self, projectName, folderName ):
        Resource.__init__( self )
        self.projectName = projectName
        self.folderName = folderName
    def getChild( self, name, request ):
        if name == "":
            return self
        else:
            return ItemResource( self.projectName, 
                                 self.folderName, 
                                 name )
    def render_GET( self, request ):
        return json.dumps( { "_type": "Folder",
                             "name": self.folderName,
                             "inProject": self.projectName } )

class ProjectResource(Resource):
    def __init__( self, projectName ):
        Resource.__init__( self )
        self.projectName = projectName
    def getChild( self, name, request ):
        if name == "":
            return self
        else:
            return FolderResource( self.projectName, name )
    def render_GET( self, request ):
        return json.dumps( { "_type": "Project",
                             "name": self.projectName } )


class ProjectIndex(Resource):
    def getChild( self, name, request ):
        print "name %r request %r" % (name,request)
        if name == "":
            return self
        else:
            return ProjectResource( name )
    def render_GET( self, request ):
        return json.dumps( { "projects": ["a","b"] } )

def setupREST( root ):
    rest = Resource()
    root.putChild( "rest", rest )
    rest.putChild( "project", ProjectIndex() )
