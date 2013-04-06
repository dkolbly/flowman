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
    pass
