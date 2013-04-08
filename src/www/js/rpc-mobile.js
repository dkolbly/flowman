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
                            postNotification( new Date(),
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
                    postNotification( new Date(), 
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

    session.getProjects = function () {
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
}
