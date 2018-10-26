$(document).ready(function() {
    namespace = '/execute';
    var project = $('#project_name').val();
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    socket.on('connect', function () {
        socket.emit('my_event', {data: '后台已连接!'});
        //socket.emit('executing', {room: $('#exec_room').val()});
    });
    socket.on('my_response', function (msg) {
        $('#log').append('<br>' + $('<div/>').text(msg.time_stamp + msg.data).html());
    });
    $('button#exec_room').click(function () {
        if ($('#exec_room').val() === 'batch_execute') {
            socket.emit('batch_executing');
        }
        else {
            socket.emit('executing', {room: $('#exec_room').val()});
        }
        return false;
    });
    $('button#disconnect').click(function () {
        socket.emit('disconnect_request');
        if ($('#exec_room').val() === 'batch_execute')
        {
            window.location.href = '/projects';
        }
        else {
            window.location.href = '/deploy/' + project;
        }
        return false;
    });
});