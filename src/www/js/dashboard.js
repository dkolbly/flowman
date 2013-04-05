
WorkflowSession = null;

function connected(session) {
    console.log( "Connected" );
    WorkflowSession = session;
    makeSession( session );
    session.didReceiveNotification = function (event) {
        postNotification( new Date(event[0]), event[1] );
    };

    postNotification( new Date(), "Connected" );

    var user = $("#loginName").val();
    if (user) {
        session.userLogin( $("#loginName").val(),
                           $("#loginPassword").val() );
    } else {
        session.anonymousLogin();
    }
    //session.userLogin( "alice", "foobar" );
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

function notificationClose() {
    notificationShown = false;
    $("#notification").fadeOut();
}

function loginSignIn() {
    var user = $("#loginName").val();
    $("#login").popup("close");
    postNotification( new Date(), "Re-authenticating as " + user );
    if (WorkflowSession) {
        WorkflowSession.close();
        WorkflowSession = null;
        initiateConnection();
    }
}

function postNotification(when,what,type,details) {
    var i = nextNotificationId++;
    notificationIndex[i] = [when,what,type,details];
    if (i > 10) {
        // scroll the list by removing the oldest element
        // that should be being shown
        var killId = "#n" + (i-11);
        $(killId).fadeOut(400,
                          function() {           
                              $(killId).remove();
                          });
    }
    
    var itemId = "n" + i;
    var whenTime = when.toTimeString().substr(0,5);
    if (!type) {
        type = "notify-normal";
    }
    var item = Mustache.render( notificationTemplate,
                                { type: type,
                                  itemId: itemId,
                                  whenTime: whenTime,
                                  what: what } );
    $("#notificationList").append( item );
    if (notificationShown) {
        $("#"+itemId).hide().fadeIn();
    } else {
        $("#notification").fadeIn();
        notificationShown = true;
    }
}

notificationTemplate = "<tr class='{{type}}' id='{{itemId}}'><td>{{whenTime}}</td><td>{{what}}</td></tr>";

function initiateConnection() {
    var windowURI = window.location;
    var wsURI = "ws://" + windowURI.hostname + ":2001";
    ab.connect( wsURI, connected, disconnected );
}

function pageLoaded() {
    // handler for when this page loads
    initiateConnection();
}

$(document).ready( pageLoaded );

