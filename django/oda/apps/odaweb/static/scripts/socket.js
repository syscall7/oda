"use strict";

//Socket IO

odaApplication.run(function($rootScope, addrBar, odbFile, odaSession, statusBar){
    var currentUser = $rootScope.currentUser;

    if (currentUser == null) {
        console.log('current user is null!');
        return;
    }

    var socket = io.connect("http://" + window.location.hostname + ":8080", {
        reconnection: false
    });

    socket.on('connect', function(){
        console.log('connected');

        socket.on('join', function(data) {
            console.log('join', data);
            addrBar.addUser(data.username);
            addrBar.updateUser(data.username, 0x403000);
            $rootScope.$broadcast('user.connect', data.username);
        });

        socket.on('cursor.change', function(e){
            addrBar.updateUser(e.username, e.offset);
        });

        socket.emit('subscribe',{
            //todo username
            username: currentUser.username,
            room: odbFile.shortName
        });

        socket.on('user.left', function(e) {
            console.log('leave', e);
            $rootScope.$broadcast('user.disconnect', e.username)
        });


        socket.on('users', function(e) {
            console.log('users', e);
            for (var i=0;i< e.users.length; i++ ) {
                addrBar.addUser(e.users[i]);
                $rootScope.$broadcast('user.connect', e.users[i]);
            }
        });

        socket.on('user.error', function(e) {
            toastr.error("Connection Error: " + e.error);
        });

        socket.on('odbfile.changed', function(e) {
            console.log('INCOMING', e);

            if (e.action == 'insertComment') {
                odbFile.addComment(e.data.offset, e.data.comment, true)
                statusBar.pushStatus(Handlebars.compile("{{ e.user.username }} updated a comment on 0x{{hex e.addr}}")({e: e}));
            }
            else if (e.action == 'makeData') {
                odbFile.makeData(e.data.offset, true);
                statusBar.pushStatus(Handlebars.compile("{{ e.user.username }} turned code into data on 0x{{hex e.addr}}")({e: e}));
            }
            else if (e.action == 'makeCode') {
                odbFile.makeData(e.data.offset, true);
                statusBar.pushStatus(Handlebars.compile("{{ e.user.username }} turned code into data on 0x{{hex e.addr}}")({e: e}));
            } else if (e.action  == 'updateFunction') {
                odbFile.updateFunction(e.data.offset, e.data.name,
                    e.data.retval, e.data.args, true);
                statusBar.pushStatus(Handlebars.compile("{{ e.user.username }} updated a function on 0x{{hex e.addr}}")({e: e}));
            } else if (e.action == 'createFunction') {
                 odbFile.createFunction(e.data.offset, e.data.name,
                    e.data.retval, e.data.args, true);
                 statusBar.pushStatus(Handlebars.compile("{{ e.user.username }} create a function on 0x{{hex e.addr}}")({e: e}));
            }
            else if (e.action == 'addStruct') {
                odbFile.addStructType(e.data.name, true);
            }
            else if (e.action == 'modifyStruct') {
                odbFile.modifyStructType(e.data.structindex, e.data.fields);
            }
            


        });


    });

    if (odaSession) {
        odaSession.on('cursor.change', function(e){
            var currentUser = $rootScope.currentUser;
            socket.emit('cursor.change',{
                username: currentUser.username,
                offset: e.offset
            });
        });
    }

    odbFile.on(ODB_EVENTS.CHANGED, function(e){
        if (e.remote) {
            return;
        }
        e.user = $rootScope.currentUser;
        socket.emit('odbfile.changed', e);
    });



});