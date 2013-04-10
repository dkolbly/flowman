
class TrackListCommand(object):
    @classmethod
    def help( cls ):
        return "List tracks"
    @classmethod
    def add_arguments( cls, p ):
        p.add_argument( "--name", "-n" )
        p.add_argument( "--owner" )
        p.add_argument( "--project", "-p" )
        p.add_argument( "--folder", "-f" )
        p.add_argument( "--inactive" )
    def __init__( self, args ):
        self.args = args
    def run( self, cnx ):
        x = cnx.rpc( "wf:openView",
                     "pullq.views.TrackView",
                     {} )
        #print "watch id = %r" % x
        #y = cnx.rpc( "wf:refreshView", x['id'] )
        #print "refresh => %r" % (y,)
        tbl = CLITable( [ { "key": "project", "label": "Project" },
                          { "key": "folder", "label": "Folder" },
                          { "key": "label", "label": "Label",
                            "align": "right" },
                          { "key": "owner.login", 
                            "label": "Login" },
                          { "key": "owner.fullname", 
                            "label": "Full Name" },
                          { "key": "url", "label": "Source Repository" } ] )
        lst = x.get('created',{}).values()
        tbl.provision( lst )
        #
        print
        if tbl.TOPBORDER:
            print tbl._break()
        print tbl._header()
        print tbl._break()
        for r in lst:
            print tbl._row( r )
        if tbl.BOTTOMBORDER:
            print tbl._break()
        print
        #
        """
        def more( topic, event ):
            print "more! %r %r" % (topic,event)
        cnx.subscribe( "wf:watch/%d" % x['id'], more )
        import time
        time.sleep(30)
        """

class CLITable(object):
    VBORDER = " "
    HBORDER = "-"
    INTERSECT = "-"
    TOPBORDER = False
    BOTTOMBORDER = False

    def __init__( self, columns ):
        self.columns = columns
        self.widths = [len(col['label']) for col in columns]
        self.formatters = []
        for col in columns:
            namelis = col['key'].split('.')
            fmt = col.get('formatter',str)
            if len(namelis) == 1:
                self.formatters.append( self.__topFmt( namelis[0], fmt ) )
            else:
                self.formatters.append( self.__deepFmt( namelis, fmt ) )
    def __topFmt( self, attr, fmt ):
        def func( row ):
            if attr in row:
                return fmt(row[attr])
            else:
                return '--'
        return func
    def __deepFmt( self, attrs, fmt ):
        def func( row ):
            try:
                for a in attrs:
                    row = row[a]
            except KeyError:
                return "--"
            return fmt(row)
        return func
    def __formatRow( self, row ):
        return [fn(row) for fn in self.formatters]
    def provision( self, rows ):
        for row in rows:
            f = self.__formatRow( row )
            for i, cell in enumerate(f):
                self.widths[i] = max( self.widths[i], len(cell) )
    def __centered( self, i, cell ):
        space = max( 0, self.widths[i] - len(cell) )
        return (" " * ((space+1)/2)) + cell + (" " * (space/2))
    def __left( self, i, cell ):
        space = max( 0, self.widths[i] - len(cell) )
        return cell + (" " * space)
    def __right( self, i, cell ):
        space = max( 0, self.widths[i] - len(cell) )
        return (" " * space) + cell
    def _row( self, row ):
        x = [self.VBORDER]
        for i, cell in enumerate( self.__formatRow( row ) ):
            a = self.columns[i].get('align','left')
            if a == 'right':
                x.append( self.__right( i, cell ) )
            elif a == 'center':
                x.append( self.__center( i, cell ) )
            else:
                x.append( self.__left( i, cell ) )
            x.append( self.VBORDER )
        return ''.join(x)
    def _header( self ):
        x = [self.VBORDER]
        for i, col in enumerate( self.columns ):
            x.append( self.__centered( i, col['label'] ) )
            x.append( self.VBORDER )
        return ''.join(x)
    def _break( self ):
        x = self.INTERSECT
        for w in self.widths:
            x += (self.HBORDER * w) + self.INTERSECT
        return x

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
        p.add_argument( "--folder", "-f" )
    def __init__( self, args ):
        self.args = args
    def run( self, cnx ):
        print "Foo => %r" % cnx.rpc( 'wf:foo', 3, 4 )
        assert self.args.url
        parms = { "label": "Hello, friend",
                  "url": self.args.url,
                  "base": self.args.base }
        cnx.rpc( "wf:createItem",
                 "Track",
                 self.args.folder,
                 parms )
    pass

__commands__ = { "track-create": TrackCreateCommand,
                 "track-list": TrackListCommand }
