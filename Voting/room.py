
##สำหรับเทสตอนรันก่อน
from flask import Flask,flash, request, render_template, redirect, session, url_for, Blueprint
from Voting.user import guestUser
import Voting.user as user
room_blueprint = Blueprint('room_blueprint', __name__, template_folder="templates", static_folder='static', static_url_path='/static')

#ต้องเป็น user ถึงจะมีสิทธิ์สร้างห้อง
def check_permission():
    return user.check_permission("User")

#สร้างห้อง (รอส่วนเบล) สร้าง round ใน session ทำมาเช็คว่าครบ 3 รอบไหม
@room_blueprint.route('/createRoom')
def create():
    status = check_permission()
    result = status
    if(status == True):
        if not "round" in session:
            session["round"] = 0
        session["role"] = "Moderator"
        result = "this is round {}".format(session["round"])
    return result

#ดูสถานะกับ round ของห้อง
@room_blueprint.route('/checkRoomStatus')
def checkroom():
    if not "round" in session:
        return "no debate created"
    return "There is a room ! This is round {}".format(session["round"])