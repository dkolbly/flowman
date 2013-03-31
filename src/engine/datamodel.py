#! /usr/bin/env python

from mongoengine import connect
from mongoengine import Document, StringField, ReferenceField
from mongoengine import DateTimeField, IntField, ListField
from mongoengine import DictField, BinaryField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField

connect( "flowman" )

class Project(Document):
    meta = { "allow_inheritance": False,
             "indexes": ["name"] }
    name = StringField( required=True, unique=True )
    label = StringField( required=True )
