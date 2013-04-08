

class TrackCreateCommand(object):
    @classmethod
    def help( cls ):
        return "Create a track"
    @classmethod
    def add_arguments( cls, p ):
        p.add_argument( "--name", "-n" )
        p.add_argument( "--url" )
        p.add_argument( "--base", "-b" )
        p.add_argument( "--owner" )
        p.add_argument( "--project", "-p" )
        p.add_argument( "--folder", "-f" )
    def __init__( self, args ):
        self.args = args
    def run( self, cnx ):
        print "Foo => %r" % cnx.rpc( 'wf:foo', 3, 4 )
        parms = { "label": "Hello, friend" }
        cnx.rpc( "wf:createItem",
                 self.args.project,
                 self.args.folder,
                 parms )
    pass

__commands__ = { "track-create": TrackCreateCommand }
