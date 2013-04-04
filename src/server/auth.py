from engine.datamodel import User
from autobahn.wamp import WampCraProtocol
import uuid

class AuthenticationManager(object):
    def getAuthExtra( self, user ):
        return { 'salt': user.passwordSalt,
                 'keylen': 32,
                 'iterations': 997 }

    def setPassword( self, user, clear ):
        user.passwordSalt = str(uuid.uuid4())
        ax = self.getAuthExtra( user )
        user.passwordHash = WampCraProtocol.deriveKey( clear, ax )

    def getUser( self, login ):
        u = User.objects( login=login )
        if len(u) == 0:
            return None
        return u[0]
        
    def getAuthSecret( self, login ):
        u = self.getUser( login )
        if u is None:
            return None
        # If you try to return a unicode object here, all hell
        # breaks loose in the depths of autobahn wamp
        return str(u.passwordHash)

