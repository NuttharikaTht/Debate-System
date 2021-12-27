from contextlib import nullcontext
from flask import Flask, request, render_template, Blueprint, session, redirect, url_for, flash
import mysql.connector
import hashlib
import threading
import atexit

login_blueprint = Blueprint('login_blueprint', __name__,template_folder='templates', static_folder='static', static_url_path='/static')

app = Flask(__name__)
    
@login_blueprint.route("/")
def login():
    return render_template("login.html")

@login_blueprint.route("/guest")
def guest():
    return render_template("guest.html")

@login_blueprint.route("/", methods=["POST"])
def process_input():
    db = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
        )

    mycursor = db.cursor()
    User = request.form["username"]
    Pass = request.form["password"]

    PassFromDB=""
    PassFromUser = hashlib.sha256(Pass.encode()).hexdigest()
    print("Encode Pass : "+PassFromUser)
    mycursor.execute("SELECT password FROM user_login WHERE username = '"+User+"'")
    for c in mycursor:
        PassFromDB = c
    print(PassFromDB)

    if(len(User) > 0 and len(Pass) > 0):
        if(PassFromUser in PassFromDB):
            session["username"]= User
            session["role"] = "User"
            result = redirect('/home')
        elif(len(PassFromDB) == 0):
            result =redirect('/guest')
        elif(PassFromUser not in PassFromDB):
            result =redirect('/guest')
        else:
            result =redirect('/guest')
    return result

@login_blueprint.route("/guest", methods=["POST"])
def yesno():
    clicked = request.form["guestmode"]
    
    if(clicked == "yes"):
        result = redirect('/home')
    elif(clicked == "no"):
        result = redirect('/')
    else:
        result = "error"

    session["username"]= ""
    session["role"] = "Guest"
    return result

@login_blueprint.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login_blueprint.login'))