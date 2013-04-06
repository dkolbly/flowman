#! /usr/bin/env python

from mongoengine import connect
from mongoengine import Document, StringField, ReferenceField
from mongoengine import DateTimeField, IntField, ListField
from mongoengine import DictField, BinaryField, FileField
from mongoengine import SequenceField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField

import datetime

connect( "flowman" )

class Project(Document):
    meta = { "allow_inheritance": False,
             "indexes": ["name"] }
    name = StringField( required=True, unique=True )
    label = StringField( required=True )
    description = StringField()
    properties = DictField()
    def __repr__( self ):
        return "<Project %s>" % (self.name,)

class User(Document):
    meta = { "indexes": ['userId'], "allow_inheritance": False }
    userId = SequenceField( required=True, sequence_name='UserId' )
    login = StringField( required=True )
    passwordSalt = StringField()
    passwordHash = StringField()
    label = StringField( required=True )
    aliases = ListField( StringField() )
    def __repr__( self ):
        return "<User %s>" % (self.login,)

class Workflow(Document):
    meta = { "allow_inheritance": False }
    inProject = ReferenceField( "Project", required=True, dbref=False )
    label = StringField( required=True )
    defn = StringField( required=True )

class Folder(Document):
    meta = { "allow_inheritance": False,
             "indexes": [("inProject","name")] }
    inProject = ReferenceField( "Project", required=True, dbref=False )
    follows = ReferenceField( "Workflow", required=True, dbref=False )
    count = IntField( required=True, default=0 )
    name = StringField( required=True )
    label = StringField( required=True )
    itemPattern = StringField( required=True, default="#%(itemInFolder)d" )
    properties = DictField()
    def __repr__( self ):
        return "<Folder %s/%s>" % (self.inProject.name,self.name)

class Item(Document):
    meta = { "indexes": [('inFolder','itemInFolder')], 
             "allow_inheritance": True }
    inFolder = ReferenceField( "Folder", required=True, dbref=False )
    itemInFolder = IntField( required=True )
    createdBy = ReferenceField( "User", required=True, dbref=False )
    audit = ListField( ReferenceField( "Audit", dbref=False ) )
    label = StringField( required=True )
    ctime = DateTimeField( required=True )
    mtime = DateTimeField( required=True )
    dtime = DateTimeField()
    state = DictField()
    def __init__( self, **kw ):
        super( Item, self ).__init__( **kw )
        t = datetime.datetime.now()
        f = self.inFolder
        f.count += 1
        self.ctime = t
        self.mtime = t
        self.label = f.itemPattern % dict( itemInFolder=f.count )
        self.itemInFolder = f.count
    def __repr__( self ):
        return "<Item %s>" % (self.label,)

class Audit(Document):
    meta = { "allow_inheritance": True }
    owner = ReferenceField( "User", dbref=False )
    openTime = DateTimeField( required=True )
    closeTime = DateTimeField()
    attachments = ListField( ReferenceField( "Attachment", dbref=False ) )

class Attachment(Document):
    meta = { "allow_inheritance": True }
    mimetype = StringField( required=True )
    tags = ListField( StringField() )
    content = FileField( required=True )
    pass

class Comment(Audit):
    pass

class Action(Audit):
    pass

class ManualAction(Action):
    pass

class SpawnAction(Action):
    child = ReferenceField( "Item", dbref=False, required=True )
    pass

class ApprovalAction(ManualAction):
    status = IntField( required=True, default=0 )
    STATUS = { 0: "Active", 1: "Approved", 2: "Rejected" }
    pass

# TODO - first-class Policy objects, to report policy violations
# and bypasses
