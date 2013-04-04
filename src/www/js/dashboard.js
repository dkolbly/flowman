
WorkflowSession = null;

function connected(session) {
    console.log( "Connected" );
    WorkflowSession = session;
    makeSession( session );
    session.didReceiveNotification = function (topic,event) {
        postNotification( new Date(event[0]), event[1] );
    };

    postNotification( new Date(), "Connected" );

    //session.anonymousLogin();
    session.userLogin( "alice", "foobar" );
/*
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
*/
}

function disconnected(code,reason) {
    console.log( "Disconnected: " + code + " (" + reason + ")" );
    if (WorkflowSession) {
        postNotification( new Date(), "Disconnected (" + code + ")" );
    }
    WorkflowSession = null;
}

function getProjects(then) {
    return WorkflowSession.getProjects();
}

nextNotificationId = 0;
notificationIndex = {};
notificationShown = false;

function postNotification(when,what) {
    var i = nextNotificationId++;
    var itemId = "n" + i;
    var whenTime = when.toTimeString().substr(0,5);
    var item = "<tr id='" + itemId + "'><td>" + whenTime + "</td><td>" + what + "</td></tr>";
    $("#notificationList").append( item );
    if (notificationShown) {
        $("#"+itemId).hide().fadeIn();
    } else {
        $("#notification").fadeIn();
        notificationShown = true;
    }
}

function pageLoaded() {
    // handler for when this page loads
    var windowURI = window.location;
    var wsURI = "ws://" + windowURI.hostname + ":2001";
    ab.connect( wsURI, connected, disconnected );
}

$(document).ready( pageLoaded );

