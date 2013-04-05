from mongoengine import Document, StringField, ReferenceField
from mongoengine import DateTimeField, IntField, ListField
from mongoengine import DictField, BinaryField, FileField
from mongoengine import SequenceField
from mongoengine import EmbeddedDocument, EmbeddedDocumentField

from engine.datamodel import Item

class Patient(Item):
    # Electronic Medical Record number
    emr = StringField( required=True )
    # patient name
    patientName = StringField( required=True )

