#! /usr/bin/env python

from mongoengine import Document, StringField, ReferenceField
from mongoengine import DateTimeField, IntField, ListField
from mongoengine import DictField, BinaryField, FileField
from mongoengine import SequenceField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField

from engine.datamodel import Item

class Submission(Item):
    """
    A submission denotes a request from a developer to integrate
    something upstream.
    """
    # instead of pointing to an external source repo, you can attach a bundle
    sourceRepo = StringField()
    destRepo = StringField( required=True )
    changeset = StringField( required=True )
    pass

class Track(Item):
    """
    A track is a repository that we are "watching" for changes,
    and provides an easy way (shortcut) for issuing submissions
    """
    sourceRepo = StringField( required=True )
    baseRepo = StringField( required=True )
    tip = ReferenceField( 'Changeset', dbref=False )
    basis = ReferenceField( 'Changeset', dbref=False )
    pass

class Changeset(Document):
    meta = { "indexes": ["changeset"],
             "allow_inheritance": False }
    changeset = StringField( required=True, unique=True )
    parent1 = ReferenceField( 'Changeset', dbref=False )
    parent2 = ReferenceField( 'Changeset', dbref=False )
    date = DateTimeField( required=True )
    author = StringField( required=True )
    comment = StringField( required=True )
    createdFiles = ListField( StringField() )
    deletedFiles = ListField( StringField() )
    updatedFiles = ListField( StringField() )
    externalReferenceId = StringField()
    def __repr__( self ):
        return "<Changeset %s>" % (self.changeset[0:12],)
    pass

