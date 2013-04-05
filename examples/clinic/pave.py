#! /usr/bin/env python

"""
Pave the clinic database
"""

from engine.datamodel import Project, User, Workflow, Folder


clinic = Project( name="clinic", label="Med Clinic" )
wf = Workflow( inProject=clinic,
               label="Patient Visit",
               defn="clinic.PatientVisit" )

opto = Folder( name="opto", label="Optometry" )
opto.save()

minor = Project( name="minor", label="Minor Emergency" )
minor.save()

