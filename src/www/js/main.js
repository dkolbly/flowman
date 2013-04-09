
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

function reloadStateFromServer() {
    // this is called when we establish or re-establish connectivity
    // to the server
    console.log( "reloading state" );
    tgrid.didReconnect();
}


// TODO... call session.openView() to populate table...

function View(selector) {
    console.log( "creating view on selector " + selector );

    var index = {};
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
                     cols: [ { "key": "project", "label": "Project" },
                             { "key": "folder", "label": "Folder" },
                             { "key": "label", "label": "Label",
                               "align": "right" },
                             { "key": "owner.login", 
                               "label": "Login" },
                             { "key": "owner.fullname", 
                               "label": "Full Name" },
                             { "key": "url", "label": "Source Repository" } ] };

    var div = $(selector);
    div.append( Mustache.render( viewTemplate, viewSpec ) );
    var tbody = $(div).find("table tbody");
    this.selection = [];

    var view = this;

    this.didReconnect = function () {
        console.log( "opening view" );
        var d = serverConnection.rpc( "wf:openView",
                                      "pullq.views.TrackView",
                                      {} );
        d.then( function (val) {
            console.log( "answer:" );
            console.log( val );
            // note, this works even if there is no 'created' attribute
            for (var k in val.created) {
                var v = val.created[k];
                var cols = [];
                for (var i = 0; i<viewSpec.cols.length; i++) {
                    var cell = v[viewSpec.cols[i].key]
                    if ((cell === undefined) || (cell === null)) {
                        cols[i] = { value: "--" }
                    } else {
                        cols[i] = { value: "" + cell }
                    }
                }
                var row = { id: k, cols: cols };
                index[k] = new ExpandableRow( view, row, tbody )
            }
        },
                function (err) {
                    view.showError(err)
                } );
    };
};

function ExpandableRow( view, row, tbody ) {
    var me = this;
    var exp = $.extend( { ncols: row.cols.length }, row );
    var rowdom = $(Mustache.render( viewSummaryRowTemplate, exp ));
    rowdom.appendTo( tbody );
    rowdom.click( function () {
        var unclick = false;
        if ((view.selection.length == 1) && (view.selection[0] == me)) {
            unclick = true;
        }

        for (var i=0; i<view.selection.length; i++) {
            view.selection[i].hide();
        }
        if (unclick) {
            view.selection = [];
            me.hide();
        } else {
            view.selection = [me];
            me.show();
        }
    } );

    var detaildom = $(Mustache.render( viewDetailTemplateFilled, exp ));
    detaildom.appendTo( tbody );
    detaildom.hide();
    var detaildiv = $(detaildom).find(".detailview");

    this.show = function () {
        rowdom.addClass( "selected" );
        detaildom.show();
        detaildiv.hide();
        detaildiv.slideDown();
    }

    this.hide = function () {
        rowdom.removeClass( "selected" );
        detaildiv.slideUp( 400, function() {
            detaildom.hide();
        } );
    }
}


viewTemplate = '\
<table class="summarytable" id="{{id}}">\
  <tr>{{#cols}}<th>{{label}}</th>{{/cols}}</tr>\
</table>';

viewSummaryRowTemplate = '\
<tr id="{{id}}">\
  {{#cols}}<td>{{&value}}</td>{{/cols}}\
</tr>';

viewDetailTemplate = '\
<tr id="{{id}}_detail" class="detailrow">\
  <td colspan="{{ncols}}" class="detailcell">\
    <div class="detailview">\
    </div>\
  </td>\
</tr>';

viewDetailTemplateFilled = '\
<tr id="{{id}}_detail" class="detailrow">\
  <td colspan="{{ncols}}" class="detailcell">\
    <div class="detailview">\
      <h3>Exceptions:</h3>\
      <table>\
        <tr>\
          <th>C</th>\
          <th>Exception</th>\
        </tr>\
        <tr>\
          <td>?</td>\
          <td><a href="#">Case 1234</a> is not closed</td>\
        </tr>\
        <tr>\
          <td>E</td>\
          <td><a href="#">K4044</a> has not been approved</td>\
        </tr>\
        <tr>\
          <td>E</td>\
          <td>Preflight build <a href="#">842pf</a> failed</td>\
        </tr>\
        <tr>\
          <td>!</td>\
          <td>Merge conflict</td>\
        </tr>\
      </table>\
      <h3>Changesets:</h3>\
      <table>\
        <tr>\
          <th>Id</th>\
          <th>S</th>\
          <th>Comment</th>\
        </tr>\
        <tr>\
          <td><a href="#">a54f0d69</a></td>\
          <td>-</td>\
          <td>{case:8688} foo the bar</td>\
        </tr>\
        <tr>\
          <td><a href="#">12345678</a></td>\
          <td>X</td>\
          <td>blech</td>\
        </tr>\
      </table>\
    </div>\
  </td>\
</tr>';

$(document).ready( pageLoaded );
