
function ServerConnection( hostname ) {
    // now, connect to the server
    var wsURI = "ws://" + hostname + ":2001";
    var servercnx = this;

    this.session = null;

    this.didReceiveNotification = function (event) {
        notificationPopup.post( new Date(event[0]), event[1] );
    };

    this.didAuthenticate  = function (user, perm) {
        console.log( "didAuthenticate:" );
        console.log( perm );
        if (perm && perm.info) {
            $("#loginButton .ui-btn-text").text( perm.info.label );
            servercnx.permissions = perm;
        } else {
            $("#loginButton .ui-btn-text").text( "Anonymous" );
        }
        loading.hide();
        this.rpc( "wf:setContext", null, null )
        reloadStateFromServer();
    };

    this.rpc = function () {
        return this.session.rpc.apply( this.session, arguments );
    };

    this.connected = function (session) {
        session.prefix( "wf", "http://rscheme.org/workflow#" );
        loading.show( "Authenticating" );

        servercnx.session = session;

        rpcAddFunctions( session, servercnx );

        notificationPopup.post( new Date(), "Connected..." );
        loading.hide();

        var user = $("#loginName").val();
        if (user) {
            session.userLogin( $("#loginName").val(),
                               $("#loginPassword").val() );
        } else {
            session.anonymousLogin();
        }
    }

    this.disconnected = function (code,reason) {
        console.log( "Disconnected: " + code + " (" + reason + ")" );
        loading.show( "Reconnecting" );
        if (self.session) {
            notificationPopup.post( new Date(), 
                                    "Disconnected (" + code + ")" );
        }
        self.session = null;
    }

    ab.connect( wsURI, this.connected, this.disconnected );
}

function rpcAddFunctions( session, delegate ) {
    session.anonymousLogin = function () {
        console.log( "doing anonymousLogin()" );
        session.authreq().then( function() {
            console.log( "doing authreq()" );
            session.auth().then( session.onAuthenticated );
        } )
    };

    session.userLogin = function (user,password) {
        console.log( "doing userLogin()" );
        session.authreq(user).then( 
            function(challenge) {
                console.log( "challenge:" );
                console.log( challenge );
                var jc = JSON.parse(challenge);
                console.log( jc );
                var secret = ab.deriveKey( password, jc.authextra );
                var sig = session.authsign( challenge, secret );
                session.auth(sig).then( 
                    function (perm) {
                        session.onAuthenticated( user, perm );
                    },
                    function (x) {
                        console.log( "failed auth:" );
                        console.log( x );
                        if (x.uri == "http://api.wamp.ws/error#invalid-signature") {
                            notificationPopup.post( new Date(),
                                                    "Incorrect password",
                                                    "notify-error",
                                                    x.desc );
                        }
                    } );
            },
            function (x) {
                console.log( "failed login:" );
                console.log( x );
                if (x.uri == "http://api.wamp.ws/error#no-such-authkey") {
                    notificationPopup.post( new Date(), 
                                            "Unknown user \"" + user + "\"",
                                            "notify-error",
                                            x.desc );
                    /*for (var i=0; i<x.detail.length; i++) {
                        console.log( x.detail[i] );
                    }*/
                }
            } );
    };

    session.onAuthenticated = function (user, perm) {
        console.log( "onAuthenticated, permissions:" );
        console.log( perm );

        session.subscribe( "http://rscheme.org/workflow#notification",
                           function (topic, event) {
                               console.log( "Got event (" + topic + "): " 
                                            + event );
                               delegate.didReceiveNotification( event );
                           } );
        delegate.didAuthenticate( user, perm );
    };

    session.makeErrorHandler = function (api,deferred) {
        return function(err) {
            console.log( "RPC Error (" + err.uri + "):" );
            console.log( err );
            notificationPopup.post( new Date(),
                                    "RPC Error: " + err.uri,
                                    "notify-error",
                                    err.detail );
            deferred.reject( "RPC Error" );
        }
    };
        

    session.rpc = function (api) {
        var deferred = when.defer();
        session.call.apply( session, arguments )
            .then( deferred.resolve,
                   session.makeErrorHandler( api, deferred ) );
        return deferred;
    };

    session.openView = function (factoryName, parms) {
        var deferred = when.defer();
        session.call( "http://rscheme.org/workflow#openView",
                      factoryName,
                      parms )
            .then( deferred.resolve,
                   session.makeErrorHandler( deferred ) );
        return deferred;
    };

    session.getProjects = function () {
        var deferred = when.defer();
        session.call( "http://rscheme.org/workflow#getProjects" )
            .then( function(ret) {
                      deferred.resolve( ret );
                   },
                   session.makeErrorHandler( deferred ) );
        return deferred;
    };
}
