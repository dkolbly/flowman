#! /usr/bin/env python
#
#  Data Access Layer
#
#  Provides an adaption between the underlying data model
#  in engine.datamodel and the application's connection
#  to it, which wants things like triggerable views

import datetime

import engine.datamodel
from engine.loader import loadDefinition
from mongoengine import Document
from engine.datamodel import Project, User, Workflow, Folder, Item
from engine.datamodel import Attachment
from engine.datamodel import Audit, Comment
from engine.datamodel import Action, ManualAction, SpawnAction, ApprovalAction

class TriggerScope(object):
    def __init__( self, cls, parentScope ):
        self.subject = cls
        self.triggers = []
        self.parentScope = parentScope
    def addTrigger( self, t ):
        self.triggers.append( t )
    def removeTrigger( self, l ):
        self.triggers.remove( l )
    def created( self, x ):
        assert isinstance( x, self.subject )
        x_id = x.id
        for t in self.triggers:
            t.didCreate( x_id, x )
        if self.parentScope is not None:
            self.parentScope.created( x )
    def updated( self, x ):
        assert isinstance( x, self.subject )
        x_id = x.id
        for t in self.triggers:
            t.didUpdate( x_id, x )
        if self.parentScope is not None:
            self.parentScope.updated( x )
    def deleted( self, x ):
        assert isinstance( x, self.subject )
        x_id = x.id
        for t in self.triggers:
            t.didDelete( x_id, x )
        if self.parentScope is not None:
            self.parentScope.deleted( x )

class TriggerManager(object):
    def __init__( self ):
        self.triggerScopes = {}
    def addScope( self, s ):
        self.triggerScopes[ s.subject ] = s
    def __buildScope( self, parentList ):
        c = parentList[0]
        # if we reach Document, that is the untriggerable root so return None
        if c is Document:
            return None
        # if we reach something that there is already a scope for, use it
        if c in self.triggerScopes:
            return self.triggerScopes[c]
        # otherwise, build one underneath the next-up parent
        p = self.__buildScope( parentList[1:] )
        s = TriggerScope( c, p )
        self.triggerScopes[c] = s
        return s
    def __findScopeFor( self, cls ):
        s = self.triggerScopes.get( cls )
        if s is not None:
            return s
        # it had better inherit from Document
        assert issubclass( cls, Document )
        s = self.__buildScope( cls.mro() )
        if s is None:
            raise RuntimeError, "Cannot build trigger scope for %r" % cls
        return s
        """
        parents = 
        # I am assuming this assertion holds; let me know if it doesn't
        assert parents[0] is cls
        # walk the parents list, looking for something that we do have
        # a trigger scope for
        for c in parents[1:]:
            if c is Document:
                break
            s = self.triggerScopes.get( c )
            if s is not None:
                # cache the result for next time
                self.triggerScopes[cls] = s
                return s
        # if we reach Document itself then we break out of the loop,
        # and that means we've been asked to trigger on something
        # for which no scope has been defined, and that is a Bad Thing
        raise RuntimeError, \
            "Class %r has no trigger scope defined" % cls
        """
    def watch( self, cls, t ):
        self.__findScopeFor( cls ).addTrigger( t )
    def unwatch( self, t ):
        self.__findScopeFor( cls ).removeTrigger( t )
    def created( self, x ):
        self.__findScopeFor( type(x) ).created( x )
    def updated( self, x ):
        self.__findScopeFor( type(x) ).updated( x )
    def deleted( self, x ):
        self.__findScopeFor( type(x) ).deleted( x )

TM = TriggerManager()

"""
TM.addScope( TriggerScope( Project ) )
TM.addScope( TriggerScope( User ) )
TM.addScope( TriggerScope( Workflow ) )
TM.addScope( TriggerScope( Folder ) )
TM.addScope( TriggerScope( Item ) )
TM.addScope( TriggerScope( Audit ) )
TM.addScope( TriggerScope( Attachment ) )

class RestrictedView(object):

    def __init__( self, user, permissions ):
        self.user = user
        self.perm = permissions
        pass

    def getProjects( self ):
        lst = []
        for p in Project.objects():
            lst.append( { 'oid': p.doc_id,
                          'name': p.name,
                          'label': p.label,
                          'description': p.description } )
        return lst
"""

workflowDefn = {}

def getWorkflowForFolder( f ):
    if f in workflowDefn:
        return workflowDefn[f]
    x = loadDefinition( f.follows.defn )
    w = x(f)
    workflowDefn[f] = w
    return w

class InvocationContext(object):
    def __init__( self, projectName, user, role ):
        self.project = projectName
        self.user = user
        self.role = role
    def getUser( self ):
        return User.objects.get( login=self.user )
    def getProject( self ):
        return Project.objects.get( name=self.project )

def createItem( ctx, className, inFolder, parms ):
    p = ctx.getProject()
    f = Folder.objects.get( inProject=p, name=inFolder )
    print "Folder %r follows %r : %s" % (f,f.follows,f.follows.defn)
    wfInstance = getWorkflowForFolder( f )
    print "==> %r" % wfInstance
    x = wfInstance.create( className, parms )
    x.inFolder = f
    x.itemInFolder = f.count
    if x.label is None:
        x.label = f.itemPattern % dict( itemInFolder=f.count )
    u = ctx.getUser()
    print "%r did create: %r" % (u,x,)
    x.owner = u
    now = datetime.datetime.now()
    f.count += 1
    f.save()
    a = Audit( owner=u,
               openTime=now,
               closeTime=now,
               tags=['wf:create'] )
    a.save()
    x.audit = [a]
    x.ctime = now
    x.mtime = now
    x.save()
    TM.created( x )

