import re

class Expander(object):
    PAT = re.compile( r"\$\{([^\}]+)\}" )
    def __init__( self, contexts ):
        self.contexts = contexts
        pass
    def lookup( self, expr ):
        for c in self.contexts:
            if expr in c.properties:
                return c.properties[expr]
        raise KeyError, expr
    def expand( self, s ):
        expanded = set()
        while True:
            m = self.PAT.search( s )
            if not m:
                return s
            if m.group(1) in expanded:
                raise RuntimeError, "Recursive expansion of ${%s}" % m.group(1)
            s = s[:m.start()] + self.lookup( m.group(1) ) + s[m.end():]
