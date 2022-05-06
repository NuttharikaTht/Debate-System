from flask import Flask, request, render_template, redirect, session, url_for, Blueprint
from flask_socketio import SocketIO, send, emit, join_room, leave_room, Namespace
import mysql.connector

vote_blueprint = Blueprint('vote_blueprint', __name__, template_folder="templates", static_folder='static', static_url_path='/static')

#connect database

def checkUserRoleinRoom(roomID):
    db = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
    )
    mycursor = db.cursor()
    User=session["username"]
    result = True
    #เช็คว่า user ที่เข้ามาอยู่ใน SupporterName ใน DB ไหม
    mycursor.execute("SELECT SupporterName FROM book_room WHERE RoomID="+roomID)
    for c in mycursor:
        SName = c
    if(User in SName):
        session["role"] = "Supporter"
        #result = redirect(url_for('vote_blueprint.cantVote',roomID=roomID))
    #เช็คว่า user ที่เข้ามาอยู่ใน ObjecttionName ใน DB ไหม
    mycursor.execute("SELECT ObjectionName FROM book_room WHERE RoomID="+roomID)
    for c in mycursor:
        OName = c
    if(User in OName):
        session["role"] = "Objection"
        #result = redirect(url_for('vote_blueprint.cantVote',roomID=roomID))
    if(session["role"] != "User"):
        result = redirect(url_for('vote_blueprint.cantVote',roomID=roomID))
    if(session["role"] == "Moderator"):
        result = redirect(url_for('mod_blueprint.controller',roomID=roomID))
    return result
    
#หน้า vote ต้องเป็น user ปกติถึงจะเข้าได้ แต่ตอนทำงานจริง ต้องมีหน้า waitingForMod เพิ่ม
#เปลี่ยนชื่อ route waiting for mod เก่่าของ support object guest เปลี่ยนเปน cantVoteUser
@vote_blueprint.route("/vote/<roomID>", methods=["GET","POST"])
def vote(roomID):
    permission = session["role"]
    print(permission)
    if(permission == "User"):
        #return redirect(url_for("vote_blueprint.votewaiting",roomID = roomID))
        return render_template('vote.html', roomID = roomID)
    elif(permission == "Moderator"):
        return redirect(url_for("mod_blueprint.vote_ongoing",roomID = roomID))
    else:
        return redirect(url_for('vote_blueprint.cantVote', roomID = roomID))

#หลัง vote แล้ว
@vote_blueprint.route("/voted/<roomID>", methods=["POST"])
def vote_finished(roomID):
    db = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
    )
    mycursor = db.cursor()
    User=session["username"]
    selection = request.form["selection"]
    result = selection
    if(result=="Agree"):
        result="1"
    elif(result=="NotAgree"):
        result="0"
    #เช็คว่า user ที่เข้ามาอยู่ใน SupporterName ใน DB ไหม
    mycursor.execute("SELECT SupporterName FROM book_room WHERE RoomID="+roomID)
    for c in mycursor:
        SName = c
    if(User in SName):
        return redirect(url_for('vote_blueprint.cantVote',roomID=roomID))
    #เช็คว่า user ที่เข้ามาอยู่ใน ObjecttionName ใน DB ไหม
    mycursor.execute("SELECT ObjectionName FROM book_room WHERE RoomID="+roomID)
    for c in mycursor:
        OName = c
    if(User in OName):
        return redirect(url_for('vote_blueprint.cantVote',roomID=roomID))
    #insert result
    mycursor.execute("insert into allscore (RoomID, username, score) values ('"+roomID+"', '"+User+"', '"+result+"');")
    db.commit()
    if(session["role"]=="User"):
        return redirect(url_for('vote_blueprint.votewaiting', roomID = roomID))
    return redirect(url_for('vote_blueprint.cantVote',roomID=roomID))

#หน้า vote เสร็จแล้ว รอรอบต่อไป
#จริง ๆ ทำอันนี้เป็นหน้ารอ mod ที่พูดถึงอันบนได้ 
# เปลี่ยนเป็นหน้ารอโหวตรอบต่อไป พอโหวตเสร็จก็กลับมาหน้านี้ เดี๋ยวมาแก้กับเปลี่ยนชื่อ path ค่า
@vote_blueprint.route("/votewaiting/<roomID>", methods=["GET","POST"])
def votewaiting(roomID):
    result = checkUserRoleinRoom(roomID)
    if(result == True):
        if not "round" in session:
            session["round"] = 0
        else: session["round"]+=1
        print("VOTER ==== 1 ====",roomID)
        return render_template('voterwaitVote.html',roomID=roomID)
    else: return result

# User ที่ไม่มีสิทธิ์โหวต
@vote_blueprint.route("/cantVoteUser/<roomID>", methods=["GET","POST"])
def cantVote(roomID):
    if not "round" in session:
        session["round"] = 0
    else: session["round"]+=1
    print("OTHER ==== 1 ====",roomID)
    return render_template('cantVote.html',roomID = roomID)
#เช็ค round user
@vote_blueprint.route("/checkUserRound")
def checkr():
    round = str(session["round"])
    return round

