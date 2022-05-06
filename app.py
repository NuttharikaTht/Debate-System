from logging import debug
from socket import socketpair
from flask import Flask, Blueprint, session, request, render_template, redirect, url_for
from __init__ import create_app, socketio

app = create_app(debug=True)

from flask import session, url_for
from flask_socketio import emit, send, join_room, leave_room

@socketio.on('message')
def handleMessage(data): #msg, room
    msg = data['msg']
    room = data['room']
    if(msg == 'startvote'):
        print("msg : {msg}")
        emit('redirect', {'url': url_for('vote_blueprint.vote',roomID=room)}, to=room)
    elif(msg == 'enddebate'):
        print("msg : {msg}")
        print("Summary ====")
        emit('redirect', {'url': url_for('mod_blueprint.summary', roomID=room)}, to=room) 
        #if(session["role"] == "User") :           
    else:
        print('Message: ' + msg)
        send(msg, to=room)

@socketio.on('join')
def on_join(room):
    """User joins a room"""
    print("==== 2 ====",room)
    #room = roomID
    join_room(room)
    print("========= User has joined ==========")
    send("User has Joined Room", room=room)
    #emit('Joined', {'message': "{username} Joined Room"}, room=room, namespace='/{room}')

@socketio.on('left')
def on_left(room):
    """User Lefted a room"""
    print("==== 3 ==== ",room)
    send("User has left", room=room)
    room = session.get('room')
    leave_room(room)
    print("User has Left ****")
    #emit('Joined', {'message': "{username} Joined Room"}, room=room, namespace='/{room}')
    
if __name__ == "__main__":
    #app.run(port=8080)
    socketio.run(app, port=8080)
    #socketio.run(app, port=int(os.environ.get('PORT', '5000')))
    #socketio.run(app, host="https://debatesystem.herokuapp.com/")
    #session.init_app(app)
    #app.run()