var server = require('http').createServer(handler);
var io = require('socket.io').listen(server);
var fs = require('fs');
var bunyan = require('bunyan');
var logger = bunyan.createLogger({name: 'socket'});
var _ = require('lodash');

logger.info('socket_app.js is starting ... ');
server.listen(8080);

function handler (req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Request-Method', '*');
    res.setHeader('Access-Control-Allow-Methods', 'OPTIONS, GET');
    res.setHeader('Access-Control-Allow-Headers', '*');

    if ( req.method === 'OPTIONS' ) {
        res.writeHead(200);
        res.end();
        return;
    }

    fs.readFile(__dirname + '/index.html',
    function (err, data) {
        if (err) {
          res.writeHead(500);
          return res.end('Error loading index.html');
        }

        res.writeHead(200);
        res.end(data);
    });
}

io.on('connection', function (socket) {
    logger.info('A New User Has Connected');

    var sendUsersInRoom = function(room) {
        io.of('/').adapter.clients([room], function(err, clients) {
            var connected = io.of('/').connected;
            var usernames = _.map(clients, function(client) {
                return {
                    username: connected[client].username,
                    lastReportedPosition: connected[client].lastReportedPosition
                };
            });

            io.to(room).emit('users', {
                users: usernames
            });

        });
    }

    socket.on('subscribe', function (data) {
        logger.info('subscribe', data);

        socket.username = data.username;


        var room = data.room;

        if (socket.usersCurrentRoom) {
            if (socket.usersCurrentRoom == room) {
                logger.info("User Attempted to Join Room Twice, ", socket.username, room);
            } else {
                logger.info("User Leaving ", socket.usersCurrentRoom, " and joining ", room);
                socket.leave(socket.usersCurrentRoom);
            }
        }

        logger.info('Joining User To Room', data, room)
        socket.join(room);
        socket.usersCurrentRoom = room;
        sendUsersInRoom(room);
    });


    // when the user disconnects.. perform this
    socket.on('disconnect', function (data) {
        logger.info("Socket Is Diconnecting", socket.usersCurrentRoom);
        setTimeout(function() {
            if (socket.usersCurrentRoom) {
                sendUsersInRoom(socket.usersCurrentRoom);
            }
        }, 100)
    });

    socket.on('document.update', function(data) {
        logger.info('A document.update arrived', socket.usersCurrentRoom, data)
        if (socket.usersCurrentRoom) {
            socket.broadcast.to(socket.usersCurrentRoom).emit('document.update', data);
        }

    });

    socket.on('user.position.update', function(data) {
        if (socket.usersCurrentRoom) {
            socket.lastReportedPosition = data;
            socket.broadcast.to(socket.usersCurrentRoom).emit('user.position.update', data);
        }
    })

    socket.on('cursor.change', function(data){
        logger.info("Cursor Changed", currentRoom, data);
        socket.broadcast.to(currentRoom).emit('cursor.change', data);
    });

    socket.on('odbfile.changed', function(data){
        logger.info("odbfile.changed", currentRoom, data);
        socket.broadcast.to(currentRoom).emit('odbfile.changed', data);
    });




});

/*
io.sockets.on('connection', function (socket) {

  console.log('A New User Has Connected');
  
  socket.on('subscribe', function(data) { 
    console.log('joined ',data);
    socket.join(data.room);
    socket.broadcast.emit('join', data); 
  });
  
  socket.on('unsubscribe', function(data) {
    console.log('left ' + data.room); 
    socket.leave(data.room); 
  });

  socket.on('comment', function (msg) {
    console.log('I received a comment ', msg);    
    socket.broadcast.emit('comment', msg);
  });
  socket.on('label', function(msg) { 
    console.log('I received a label ',msg);
    socket.broadcast.emit('label', msg);
  });

  socket.on('disconnect', function () {
    io.sockets.emit('user disconnected');
  });



});
*/
