
CACHE = {}

def loadDefinition( n ):
    if n in CACHE:
        return CACHE[n]
    x = n.split('.')
    m = __import__( '.'.join(x[:-1]) )
    for step in x[1:]:
        m = getattr( m, step )
    CACHE[n] = m
    return m

