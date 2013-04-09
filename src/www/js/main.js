
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

    // putting this here for now... should be in a page-specific section
    tgrid = new View( "#tracksGrid" );
};

function View(selector) {
    console.log( "creating view on selector " + selector );
    var data = [];
    d0 = {};
    d0["id"] = "m101";
    d0["name"] = "donovan3";
    d0["owner"] = "donovan";
    d1 = {};
    d1["id"] = "m444";
    d1["name"] = "lane-beta";
    d1["owner"] = "lane";
    data[0] = d0;
    data[1] = d1;

    var viewSpec = { id: "v99",
                     cols: [ { label: "Foo" },
                             { label: "Bar" },
                             { label: "Comment" } ] };
    var div = $(selector);
    div.append( Mustache.render( viewTemplate, viewSpec ) );
    var tbody = $(div).find("table tbody");

    var row = { id: "v99_1",
                cols: [ { "value": "<a href='#'>a54f0d69</a>" },
                        { "value": "-" },
                        { "value": "A silly thing, nothing really" } ] };
    var rowdom = $(Mustache.render( viewSummaryRowTemplate, row ));
    rowdom.appendTo( tbody );

    var row = { id: "v99_2",
                cols: [ { "value": "<a href='#'>12345678</a>" },
                        { "value": "?" },
                        { "value": "What up homey?" } ] };
    var rowdom = $(Mustache.render( viewSummaryRowTemplate, row ));
    rowdom.appendTo( tbody );
};

viewTemplate = '\
<table class="sumarytable" id="{{id}}">\
  <tr>{{#cols}}<th>{{label}}</th>{{/cols}}</tr>\
</table>';

viewSummaryRowTemplate = '\
<tr id="{{id}}">\
  {{#cols}}<td>{{&value}}</td>{{/cols}}\
</tr>';
$(document).ready( pageLoaded );
