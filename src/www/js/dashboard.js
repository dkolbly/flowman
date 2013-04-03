
WorkflowSession = null;

function connected(session) {
    console.log( "Connected" );
    WorkflowSession = session;
    WorkflowSession.getProjects = function () {
        var deferred = when.defer();
        session.call( "http://rscheme.org/workflow#getProjects" )
            .then( function(ret) {
                      deferred.resolve( ret );
                   },
                   function(err,desc) {
                       console.log( "RPC Error:" );
                       console.log( err );
                       console.log( desc );
                       deferred.reject( "RPC Error" );
                   } );
        return deferred;
        };
    $(".status").html( "Connected" );

    // load up state from the server
    var p = WorkflowSession.getProjects();
    when( p, function (projects) {
        console.log( projects );
        for (var i = 0; i<projects.length; i++) {
            var p = projects[i];
            console.log( p );
            $("#projectList").append('<li><a id="' + p.name + '">' + p.label + '</a></li>');
        };
        $("#projectList").listview('refresh');
    } );

}

function disconnected(code,reason) {
    console.log( "Disconnected: " + code + " (" + reason + ")" );
    WorkflowSession = null;
    $(".status").html( "<i>Disconnected (" + code + ")</i>" );
}

function getProjects(then) {
    return WorkflowSession.getProjects();
}

function postNotification(what) {
    x = $("#notificationList").append( "<li><span>" + what + "</span></li>" );
    // x is not the object I think it should be...
    x.hide();
    x.fadeIn();
}

function pageLoaded() {
    // handler for when this page loads
    var wsURI = "ws://localhost:2001";
    ab.connect( wsURI, connected, disconnected );
}

$(document).ready( pageLoaded );

