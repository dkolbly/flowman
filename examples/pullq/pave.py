#! /usr/bin/env python

"""
Pave a dev environment database
"""

from engine.datamodel import Project, User, Workflow, Folder

rel = Project( name="rel", label="Release" )
rel.save()

sbx = Project( name="sbx", label="Sandbox" )
sbx.save()

pr = Workflow( inProject=rel,
               label="Pull Request",
               defn="pullq.wf.PullRequest" )
pr.save()

br = Workflow( inProject=rel,
               label="Build Release",
               defn="pullq.wf.BuildRelease" )
br.save()

tr = Workflow( inProject=rel,
               label="Repo Tracking",
               defn="pullq.wf.Tracking" )
tr.save()

# here we are demonstrating that a project
# can contain folders that follow different workflows

sprint13 = Folder( inProject=rel,
                   name="sprint13", 
                   label="Sprint 13",
                   follows=pr )
sprint13.save()

tracks = Folder( inProject=rel,
                 name="tracks",
                 label="Tracks",
                 follows=tr )
tracks.save()

v1_0 = Folder( inProject=rel,
               name="1.0",
               label="1.0 Beta",
               follows=br )
v1_0.save()

from server.auth import AuthenticationManager
auth = AuthenticationManager()

admin = User( login="admin", label="Administrator" )
auth.setPassword( admin, "admin" )
admin.save()
