
/* Bugs:

   - sometimes the Projects list doesn't get cleared out and will
     get multiple copies of projects.  check when the server goes
     up and down, and when doing login/logout from main page

   - the Role list is not populated from the permissions.info object

   - highlighting of the currently selected project doesn't work when
     returning to the options page

   - reconnecting ("loading") dialog sticks around when autobahn.js finally
     gives up

   - need complete rewrite for better data abstraction!
*/


WorkflowSession = null;
selectedProjectOid = null;

function projectSelect(x) {
    console.log( "project selection: " + x.id );
    selectedProjectOid = x.id;
    reloadStateFromServer();
}

projectEntryTemplate = '<li data-theme="{{theme}}"><a id="{{oid}}" href="#options" onclick="projectSelect(this)"><h3>{{label}}</h3><p>{{description}}</p></a></li>';

itemEntryTemplate = '<li><a id="{{oid}}" href="p/{{projectName}}/{{folderName}}/{{itemInFolder}}/" onclick="projectSelect(this)"><h3>{{label}}</h3><p>{{description}}</p></a></li>';

function reloadStateFromServer() {
    console.log( "reloading state" );
    // reload our state from the server
    var p = WorkflowSession.getProjects();
    console.log( p );
    when( p, function (projects) {
        $("#projectList .li").remove();
        console.log( projects );
        for (var i = 0; i<projects.length; i++) {
            var p = jQuery.extend( {}, projects[i] );
            if (p.oid == selectedProjectOid) {
                p.theme = "b";
            } else {
                p.theme = "c";
            }
            $("#projectList").append( Mustache.render( projectEntryTemplate, 
                                                       p ) );
        };
        $("#projectList").listview('refresh');
    } );
};

function connected(session) {
    $.mobile.loading( 'show', { theme:"b", 
                                text:"Authenticating",
                                textVisible: true } );
    console.log( "Connected" );
    WorkflowSession = session;
    rpcAddFunctions( session, session );
    session.didReceiveNotification = function (event) {
        postNotification( new Date(event[0]), event[1] );
    };

    session.didAuthenticate = function (user, perm) {
        console.log( "didAuthenticate:" );
        console.log( perm );
        if (perm && perm.info) {
            $("#loginButton .ui-btn-text").text( perm.info.label );
            session.permissions = perm;
        } else {
            $("#loginButton .ui-btn-text").text( "Anonymous" );
        }
        $.mobile.loading( 'hide' );
        reloadStateFromServer();
    };

    postNotification( new Date(), "Connected..." );

    var user = $("#loginName").val();
    if (user) {
        session.userLogin( $("#loginName").val(),
                           $("#loginPassword").val() );
    } else {
        session.anonymousLogin();
    }
}

function disconnected(code,reason) {
    console.log( "Disconnected: " + code + " (" + reason + ")" );
    $.mobile.loading( 'show', { theme:"b", 
                                text:"Reconnecting",
                                textVisible: true } );
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
    $.mobile.loading( 'show', { theme:"b", 
                                text:"Connecting",
                                textVisible: true } );
    initiateConnection();
}

$(document).ready( pageLoaded );

