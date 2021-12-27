from contextlib import nullcontext
from flask import Flask, request, render_template, Blueprint, session, url_for
import mysql.connector
import jwt
import requests
import json
from time import time
import datetime

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import Voting

from werkzeug.utils import redirect

bookroom_blueprint = Blueprint('bookroom_blueprint', __name__,template_folder='templates', static_folder='static', static_url_path='/static')

app = Flask(__name__)

#ต้องเป็น user ถึงจะมีสิทธิ์สร้างห้อง
def check_permission():
    return Voting.user.check_permission("User")

@bookroom_blueprint.route('/book')
def home():
    status = check_permission()
    if(status == True):
        if not "round" in session:
            session["round"] = 0
        session["role"] = "Moderator"
        return render_template("BookaDate.html")
    else:
        return status

@bookroom_blueprint.route('/book', methods=["POST"])
def bookroom():
    if(check_permission):
        conn = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
    )

    supporter = request.form["ipsup"]
    opposition = request.form["ipopp"]
    
    cur = conn.cursor()
    cur.execute("SELECT username FROM user_login WHERE username = '"+supporter+"'")
    usersup = cur.fetchall()

    bur = conn.cursor()
    bur.execute("SELECT username FROM user_login WHERE username = '"+opposition+"'")
    useropp = cur.fetchall()

    if not usersup and not useropp:
        session["role"] = "User"
        session.pop("round",None)
        result = "Don't have this usersname supporter and oppositer"
    elif usersup and not useropp:
        session["role"] = "User"
        session.pop("round",None)
        result = "Don't have this usersname oppositer"
    elif not usersup and useropp:
        session["role"] = "User"
        session.pop("round",None)
        result = "Don't have this usersname supporter"
    else:
        # Enter your API key and your API secret
        API_KEY = 'C7ACOaLITyKVmrkCe_PSyg'
        API_SEC = 'WzxpprVlV2od2Fshg7kby9oPaiRJBhKAi65k'

        token = jwt.encode(
		
            # Create a payload of the token containing
            # API Key & expiration time
            {'iss': API_KEY, 'exp': time() + 5000},
            
            # Secret used to generate token signature
            API_SEC,
            
            # Specify the hashing alg
            algorithm='HS256'
        )
    
        topic = request.form["iptopic"]
        dd = int(request.form["ipday"])
        mm = int(request.form["ipmonth"])
        yy =int(request.form["ipyear"])

        t = request.form["iptime"]

        times = t.split(':', 1)
        hour = int(times[0])
        minute = int(times[1])

        dates = datetime.datetime(yy,mm,dd,hour,minute).strftime("%Y-%m-%dT%H:%M:%S")

        datebook = request.form["ipyear"]+"-"+request.form["ipmonth"]+"-"+request.form["ipday"]

        meetingdetails = {"topic": topic,
                                            "type": 2,
                                            "start_time": dates,
                                            "duration": "30",
                                            "agenda": "test",

                                            "recurrence": {"type": 1,
                                                                        "repeat_interval": 1
                                                                        },
                                            "settings": {"host_video": "true",
                                                                                "participant_video": "true",
                                                                                "join_before_host": "False",
                                                                                "mute_upon_entry": "False",
                                                                                "watermark": "true",
                                                                                "audio": "voip",
                                                                                "auto_recording": "cloud"
                                                                                }
                                            }
        # send a request with headers including
        # a token and meeting details
        roomID = ""
        headers = {'authorization': 'Bearer %s' % token,
                    'content-type': 'application/json'}
        r = requests.post(
            f'https://api.zoom.us/v2/users/me/meetings',
        headers=headers, data=json.dumps(meetingdetails))

        # print(r.text)
        # converting the output into json and extracting the details
        y = json.loads(r.text)
        join_URL = y["join_url"]
        meetingPassword = y["password"]

        url = str(join_URL)
        zoomPass = str(meetingPassword)

        mycursor = conn.cursor()
        mycursor.execute("insert into book_room (date, time, Title, SupporterName, ObjectionName, ZoomLink, ZoomPassword) values ('"+datebook+"','"+t+"','"+topic+"','"+supporter+"','"+opposition+"','"+url+"', '"+zoomPass+"');")
        conn.commit()

        #data=[]
        mycursor.execute("select RoomId from book_room where date='"+datebook+"' and time='"+t+"' and Title='"+topic+"' and SupporterName='"+supporter+"' and ObjectionName='"+opposition+"' and ZoomLink='"+url+"' and ZoomPassword='"+zoomPass+"'")
        result = mycursor.fetchall()
        for row in result:
            #data.append({'roomID' : row[0]})
            roomID = row[0]
        
        result = redirect(url_for('mod_blueprint.controller', roomID=roomID))
        session["round"] = 0
        session["role"] = "Moderator"
    return result

#ดูสถานะกับ round ของห้อง
@bookroom_blueprint.route('/checkRoomStatus')
def checkroom():
    if not "round" in session:
        return "no debate created"
    return "There is a room ! This is round {}".format(session["round"])

#app.register_blueprint(bookroom_blueprint)

if __name__ == "__main__":
    app.run(debug=True)