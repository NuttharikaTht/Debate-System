from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(debug = True):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecret'
    
    from login.login import login_blueprint
    from Voting.voting import vote_blueprint
    from Voting.Moderator import mod_blueprint
    from Voting.room import room_blueprint
    from Voting.user import user_blueprint
    from debateRoom.debate import debate_blueprint
    from Bookroom.bookroom import bookroom_blueprint
    
    app.register_blueprint(login_blueprint)
    app.register_blueprint(vote_blueprint)
    app.register_blueprint(mod_blueprint)
    app.register_blueprint(room_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(debate_blueprint)
    app.register_blueprint(bookroom_blueprint)
    socketio.init_app(app, cors_allowed_origins='*')
    
    return app
