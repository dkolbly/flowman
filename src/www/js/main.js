
loading = new function() {
    this.shown = false;
    this.show = function (msg) {
        $("#loadingtext").text( msg );
        if (!this.shown) {
            this.shown = true;
            $("#loading").fadeIn();
        }
    }
    this.hide = function (msg) {
        this.shown = false;
        $("#loading").fadeOut();
    }
};

function NotificationPopup() {
    var div = $("#notification");
    var button = $("#openNotification");
    this.div = div;

    //button.addClass( "notify-unread" );
    button.button( {
        icons: {
            primary: "ui-icon-alert"
        }
    } ).click( function() {
        div.fadeIn();
        numUnread = 0;
        $("#openNotification span.ui-button-text").text( 0 );
        button.removeClass( "notify-unread" );
    } );

    var notificationTemplate = "<tr class='{{type}}' id='{{itemId}}'><td>{{whenTime}}</td><td>{{what}}</td></tr>";

    var numUnread = 0;
    var nextNotificationId = 0;
    var notificationIndex = {};
    var notificationShown = false;

    this.post = function(when,what,type,details) {
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
        numUnread++;
        $("#openNotification span.ui-button-text").text( numUnread );
        if (numUnread == 1) {
            button.addClass( "notify-unread" );
        }
        var item = Mustache.render( notificationTemplate,
                                    { type: type,
                                      itemId: itemId,
                                      whenTime: whenTime,
                                      what: what } );
        $("#notificationList").append( item );
        /*
        if (notificationShown) {
            $("#"+itemId).hide().fadeIn();
        } else {
            $("#notification").fadeIn();
            notificationShown = true;
        }*/
    }

    $("#notificationClose").button( {
        icons: { 
            primary: "ui-icon-circle-close"
        },
        text: false
    }).click( function() {
        notificationShown = false;
        div.fadeOut();
    } );
}

function ModalDialog( button, dialog, buttonopts ) {
    this.button = button;
    this.dialog = dialog;

    this.button.button( buttonopts ).click( function(event) {
        dialog.dialog( "open" );
    } );

    this.dialog.dialog({
        autoOpen: false,
        width: 400,
        modal: true,
        buttons: [ {
            text: "OK",
            click: function() {
                $(this).dialog( "close" );
            }
        }, {
            text: "Cancel",
            click: function() {
                $(this).dialog( "close" );
            }
        } ]
    });
}

function pageLoaded() {
    $("#mobileLink").tooltip();

    notificationPopup = new NotificationPopup();

    optionsDialog = new ModalDialog( $("#openOptions"),
                                     $("#options"),
                                     {
                                         icons: {
                                             primary: "ui-icon-gear"
                                         }
                                     } );
    
    loginDialog = new ModalDialog( $("#openLogin"),
                                   $("#login"),
                                   {
                                       icons: {
                                           secondary: "ui-icon-triangle-1-s"
                                       }
                                   } );

    serverConnection = new ServerConnection( window.location.hostname );

    // refresh elements with class "timeago" every few seconds
    var timeagoLoop = function () {
        refreshTimeAgos();
        setTimeout( timeagoLoop, 6000 );
    }
    timeagoLoop();
    
    // putting this here for now... should be in a page-specific section
    tgrid = new View( "#tracksGrid" );
};

function reloadStateFromServer() {
    // this is called when we establish or re-establish connectivity
    // to the server
    console.log( "reloading state" );
    tgrid.didReconnect();
}


function timeAgoString(t) {
    var currentTime = new Date().valueOf();
    var ago = (currentTime - t) * 0.001;
    if (ago < 120) {
        return "just now";
    } else if (ago < 2*60) {
        return (ago.toFixed(1)) + " seconds ago";
    } else if (ago < 2*3600) {
        return ((ago / 60).toFixed(1)) + " minutes ago";
    } else if (ago < 2*86400) {
        return ((ago / 3600).toFixed(1)) + " hours ago";
    } else {
        return ((ago / 86400).toFixed(1)) + " days ago";
    }
}

function refreshTimeAgos() {
    lst = $(".timeago");
    for (var i=0; i<lst.length; i++) {
        // the absolute time is stored in the title of the node
        var abstime = new Date( lst[i].title );
        $(lst[i]).text( timeAgoString(abstime.valueOf()) );
    }
}

$(document).ready( pageLoaded );
