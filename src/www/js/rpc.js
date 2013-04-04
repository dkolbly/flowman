
function makeSession( session ) {
    session.anonymousLogin = function () {
        console.log( "doing anonymousLogin()" );
        session.authreq().then( function() {
            console.log( "doing authreq()" );
            session.auth().then( session.onAuthenticated );
        } )
    };

    session.userLogin = function (user,password) {
        console.log( "doing userLogin()" );
        session.authreq(user).then( function(challenge) {
            console.log( "challenge:" );
            console.log( challenge );
            var jc = JSON.parse(challenge);
            console.log( jc );
            var secret = ab.deriveKey( password, jc.authextra );
            var sig = session.authsign( challenge, secret );
            session.auth(sig).then( session.onAuthenticated );
        } )
    };

    session.didReceiveNotification = function (topic,event) {
    };

    session.onAuthenticated = function (perm) {
        console.log( "onAuthenticated, permissions:" );
        console.log( perm );

        session.subscribe( "http://rscheme.org/workflow#notification",
                           function (topic, event) {
                               console.log( "Got event (" + topic + "): " 
                                            + event );
                               session.didReceiveNotification( topic, event );
                           } );

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
