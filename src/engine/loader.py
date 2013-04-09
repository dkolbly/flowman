
def loadDefinition( n ):
    x = n.split('.')
    m = __import__( '.'.join(x[:-1]) )
    for step in x[1:]:
        m = getattr( m, step )
    return m

