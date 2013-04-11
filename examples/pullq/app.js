
function TrackView() {
    this.headlineTemplate = '\
<tr id="{{id}}">\
  <td>{{project}}</td>\
  <td>{{folder}}</td>\
  <td>{{label}}</td>\
  <td>{{ownerlogin}}</td>\
  <td>{{ownername}}</td>\
  <td>{{url}}</td>\
</tr>';

    this.detailTemplate = '\
    <div>\
      <h3>Exceptions:</h3>\
      <table>\
        <tr>\
          <th>C</th>\
          <th>Exception</th>\
        </tr>\
{{#exceptions}}\
        <tr>\
          <td>{{severity}}</td>\
          <td>{{&summary}}</td>\
        </tr>\
{{/exceptions}}\
      </table>\
      <h3>Changesets:</h3>\
      <table>\
        <tr>\
          <th>Id</th>\
          <th>S</th>\
          <th>Date</th>\
          <th>Comment</th>\
        </tr>\
{{#changesets}}\
        <tr>\
          <td><a href="http://project.fogbugz.com/#{{id}}">{{id}}</a></td>\
          <td>{{status}}</td>\
          <td><a class="timeago" title="{{date}}">{{ago}}</a></td>\
          <td>{{&comment}}</td>\
        </tr>\
{{/changesets}}\
      </table>\
      <h3>Actions:</h3>\
      <a title="[left]" class="actionbutton">Go Left</button>\
      <a title="[reactivate]" class="actionbutton">Reactivate</button>\
      <a title="[close]" class="actionbutton">Close</button>\
    </div>';

    this.headline = function (h) {
        // return an object suitable for composition with the template
        // for a headline object, 
        return { project: h.project,
                 folder: h.folder,
                 label: h.label,
                 ownerlogin: h.owner.login,
                 ownername: h.owner.fullname,
                 url: h.url }
    }
    this.details = function (d) {
        // return an object suitable for composition with the template
        // for a detail div
        for (var i=0; i<d.changesets.length; i++) {
            var c = d.changesets[i];
            c.ago = timeAgoString( c.time );
            c.date = new Date( c.time ).toLocaleString();
        }
        return d;
    }
}
