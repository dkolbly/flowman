function View(selector) {
    console.log( "creating view on selector " + selector );

    var index = {};
    var data = [];

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
    // build getters
    for (var i=0; i<viewSpec.cols.length; i++) {
        var expr = "x." + viewSpec.cols[i].key;
        viewSpec.cols[i].getter = eval( "(function(x){return " + expr + "})" );
    }

    var div = $(selector);
    div.append( Mustache.render( viewTemplate, viewSpec ) );
    var tbody = $(div).find("table tbody");
    this.selection = [];
    this.detailsTemplate = null;

    var view = this;

    this.didReconnect = function () {
        console.log( "opening view" );
        var d = serverConnection.rpc( "wf:openView",
                                      "pullq.views.TrackView",
                                      {} );
        d.then( function (val) {
            console.log( "answer:" );
            console.log( val );
            view.watchId = val.id;
            // note, this works even if there is no 'created' attribute
            for (var k in val.created) {
                var v = val.created[k];
                var cols = [];
                for (var i = 0; i<viewSpec.cols.length; i++) {
                    var cell = viewSpec.cols[i].getter(v);
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

    var detaildom = $(Mustache.render( viewDetailTemplate, exp ));
    detaildom.appendTo( tbody );
    detaildom.hide();
    var detaildiv = $(detaildom).find(".detailview");

    this.show = function () {
        rowdom.addClass( "selected" );
        loading.show( "Getting details" );
        var needTemplate = false;
        if (view.detailsTemplate === null) {
            needTemplate = true;
        }
        var d = serverConnection.rpc( "wf:getDetails",
                                      view.watchId,
                                      row.id,
                                      needTemplate );
        d.then( function (rsp) {
            console.log( "got details:" );
            console.log( rsp );
            loading.hide();
            detaildom.show();
            var template = view.detailsTemplate;
            if (rsp.template) {
                template = rsp.template;
                view.detailsTemplate = template;
            }
            detaildiv.html( Mustache.render( template, rsp.details ) );
            detaildiv.find("div .actionbutton")
                .button()
                .click( function(event) {
                    // this is a little hacky... extract the action keyword
                    // from the element's title text by looking for the last
                    // "[thing]"
                    var openbr = this.title.lastIndexOf( "[" );
                    var trailer = this.title.substr( openbr+1 );
                    var closebr = trailer.search( "]" );
                    var action = trailer.substr(0,closebr);
                    console.log( "Action = <" + action + ">" );
                } );

            detaildiv.hide();
            detaildiv.slideDown();
        },
                function (err) {
                    loading.hide();
                } );
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
