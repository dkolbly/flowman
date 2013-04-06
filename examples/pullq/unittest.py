
from engine.datamodel import Project, User, Workflow, Folder
from data import Track
import datetime

p = Project.objects.get( name="rel" )
f = Folder.objects.get( inProject=p, name="sprint13" )
u = User.objects.get( login="admin" )

t = Track( inFolder=f,
           createdBy=u,
           label="donovan",
           ctime=datetime.datetime.now(),
           mtime=datetime.datetime.now() )

#sourceRepo=
