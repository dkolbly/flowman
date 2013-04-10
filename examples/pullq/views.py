from server.views import View
from engine.datamodel import User
from data import Track

class TrackView(View):
    subject = Track

    def buildPreFilter( self, parms ):
        f = { "active": True }
        if 'owner' in parms:
            u = User.objects.get( login=parms['owner'] )
            f["owner"] = u
        return f

    def buildPostPredicate( self, parms ):
        return lambda x: True

    def buildFullPredicate( self, parms ):
        if 'owner' in parms:
            uid = User.objects.get( login=parms['owner'] ).id
            return lambda x: x.active and (x.owner.id == uid)
        else:
            return lambda x: x.active

    def headlineform( self, k, b, x ):
        return { "project": x.inFolder.inProject.name,
                 "folder": x.inFolder.name,
                 "label": x.label,
                 "url": x.sourceRepo,
                 "owner": { "login": x.owner.login,
                            "fullname": x.owner.label } }
    def detaildivtemplate( self ):
        return TRACK_DETAIL_TEMPLATE
    def detailform( self, k, b, x ):
        excList = [ { "severity": "?",
                      "summary": "What are you talking about?" } ]
        changesetList = [ { "id": "c55316e326",
                            "author": "alice",
                            "status": "",
                            "comment": "Fixing some nice things" } ]
        caseList = []
        return { "exceptions": excList,
                 "changesets": changesetList,
                 "cases": caseList }

TRACK_DETAIL_TEMPLATE = """
    <div>
      <h3>Exceptions:</h3>
      <table>
        <tr>
          <th>C</th>
          <th>Exception</th>
        </tr>
{{#exceptions}}
        <tr>
          <td>{{severity}}</td>
          <td>{{&summary}}</td>
        </tr>
{{/exceptions}}
      </table>
      <h3>Changesets:</h3>
      <table>
        <tr>
          <th>Id</th>
          <th>S</th>
          <th>Comment</th>
        </tr>
{{#changesets}}
        <tr>
          <td><a href="http://project.fogbugz.com/#{{id}}">{{id}}</a></td>
          <td>{{status}}</td>
          <td>{{&comment}}</td>
        </tr>

{{/changesets}}
        <tr>
          <td><a href="#">a54f0d69</a></td>
          <td>-</td>
          <td>{case:8688} foo the bar</td>
        </tr>
        <tr>
          <td><a href="#">12345678</a></td>
          <td>X</td>
          <td>blech</td>
        </tr>
      </table>
      <h3>Actions:</h3>
      <a title="[left]" class="actionbutton">Go Left</button>
      <a title="[reactivate]" class="actionbutton">Reactivate</button>
      <a title="[close]" class="actionbutton">Close</button>
    </div>
"""
