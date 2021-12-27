import Voting.user as user
from flask import Flask,flash, request, render_template, redirect, session, url_for, Blueprint
import mysql.connector
import requests


#ทำ blueprints เพื่อเอาไปรันบน route หลักที่ app.py
mod_blueprint = Blueprint('mod_blueprint', __name__, template_folder="templates", static_folder='static', static_url_path='/static')
global lists
lists = []
#ใช้ check permission จาก user
def check_permission():
    return user.check_permission("Moderator")

#เช็คโหมวด เวลากดปุ่มมา ว่าจะไปหน้าไหนต่อ
def check_mode(clicked, roomID):
    if(clicked == "startvote"):
        return url_for('mod_blueprint.vote_ongoing',roomID = roomID)
    if(clicked == "endvote"):
        return url_for('mod_blueprint.vote_close',roomID = roomID, list=lists)
    if(clicked == "backtocontroller"):
        return url_for('mod_blueprint.controller',roomID =roomID)
    if(clicked == "enddebate"):
        if(session["round"] >= 3):
            return url_for('mod_blueprint.summary',roomID= roomID)
        else:
            return url_for('mod_blueprint.more_round',roomID = roomID)
        
def sumdb(roomID):
    db = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
    )
    mycursor = db.cursor()
    session["role"] = "User"
    session.pop('round', None)

    #Count Support Score
    mycursor.execute("select count(score) from allscore where RoomID='"+roomID+"'and score=1")
    for c in mycursor:
        SScore = c
    print(SScore[0])

    #Count Object Score
    mycursor.execute("select count(score) from allscore where RoomID='"+roomID+"'and score=0")
    for c in mycursor:
        OScore = c
    print(OScore[0])
    lists=[]
    lists.append({                
        'SScore': str(SScore[0]),
        'OScore': str(OScore[0])
    })
    return lists

#หน้า controller mod เข้าได้คนเดียว

@mod_blueprint.route("/controller/<roomID>")
def controller(roomID):
    status = check_permission()
    session["roomID"] = roomID
    result = status
    if(status == True):
        if not "round" in session:
            result = "no debate created"
        print("MOD ===== 1 =====")
        result = render_template("controller.html", roomID=roomID)
    return result

#หน้า controller ส่วน POST หลังกดปุ่มมาแล้ว เช็คว่าจะไปไหนต่อ
@mod_blueprint.route("/controller/<roomID>", methods=["POST"])
def process(roomID):
    status = check_permission()
    result = status
    if(status == True):
        clicked = request.form["controller"]
        print(clicked)
        result = redirect(check_mode(clicked, roomID))
    return result

#หน้ากำลังโหวต vote กำลังเริ่มอยู่ มีให้กด end vote
@mod_blueprint.route("/vote_ongoing/<roomID>", methods=["GET","POST"])
def vote_ongoing(roomID):
    status = check_permission()
    result = status
    if(status == True):
        if(request.method == "POST"):
            clicked = request.form["controller"]
            print(clicked)
            result = redirect(check_mode(clicked, roomID))
        else: result = render_template('modVotestarted.html')
    return result

#หลังกด endvote redirect ไปต่อที่หน้า close vote
#หลังกด end vote round debate เพิ่มขึ้น 1 แสดงตารางสรุปผลของรอบนัั้น
@mod_blueprint.route("/vote_close/<roomID>", methods=["GET","POST"])
def vote_close(roomID):
    status = check_permission()
    result = status
    if(status == True):
        if(request.method == "POST"):
            clicked = request.form["controller"]
            print("closing vote...")
            result = redirect(check_mode(clicked, roomID))
        else:
            session["round"]+=1
            roomID = session["roomID"]
            result = render_template('modVoteclosed.html')
    return result

#round ไม่ถึง 3 รอบ รันหน้ามีปุ่มให้กดกลับไป controller 
@mod_blueprint.route("/more_round/<roomID>", methods=["GET","POST"])
def more_round(roomID):
    status = check_permission()
    result = status
    if(status == True):
        if(request.method == "POST"):
            clicked = request.form["controller"]
            roomID = session["roomID"]
            result = redirect(check_mode(clicked, roomID))
        else :
            result = render_template('moreRound.html', roomID=roomID)
    return result

#หลังกดปุ่ม redirect กลับไป controller


#ปิดโหวตแต่ละรอบ หลังกดปุ่มมาจาก controller


#ปิดดีเบต แสดงตารางสรุปคะแนน
@mod_blueprint.route("/summary/<roomID>", methods=["GET", "POST"])
def summary(roomID):
    #connect database
    if(session["round"]>=3):
        lists = sumdb(roomID)
        return render_template('summary.html', lists=lists)
    else:
        if(session["role"]=="Moderator"):
            return redirect(url_for('mod_blueprint.more_round',roomID = roomID))
        else:
            session["round"]-=1
            return redirect(url_for('vote_blueprint.votewaiting',roomID = roomID))
    
    
#app.register_blueprint(mod_blueprint)
#if __name__ == "__main__": 
#    app.secret_key = 'BAD_SECRET_KEY'
#    app.run(host='0.0.0.0')
