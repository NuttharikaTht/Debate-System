
##สำหรับเทสตอนรันก่อน
from flask import Flask,flash, request, render_template, redirect, session, url_for, Blueprint

user_blueprint = Blueprint('user_blueprint', __name__, template_folder="templates", static_folder='static', static_url_path='/static')

#เช็ค permission ของ user
def check_permission(allowed_role):
    guestUser()
    if(session["role"] == allowed_role):
        return True
    return render_template('permissionDenied.html')

#ถ้าไม่ได้ login เข้ามา จะเซ็ต username กับ role เป็นตามด้านล่าง
def guestUser():
    if (not "username" in session) or (not "role" in session):
        session["username"] = "guest"
        session["role"] = "GuestUser"
    return session["role"]

#เข็คว่า user ที่ล้อกอินอยู่เป็นใคร มี role อะไรตอนนั้น
@user_blueprint.route('/checkUserStatus')
def check_status():
    result = guestUser()
    return session["username"] + " " + session["role"]

#ทำมาเทส เปลี่ยนโรลสำหรับ user ที่ login เข้ามา
@user_blueprint.route('/changeRole', methods= ["GET"])
def selectRole():
    result = guestUser()
    if(result == "GuestUser"):
        return result
    return render_template('selectRole.html')

#หลังกดปุ่มเปลี่ยน role
@user_blueprint.route('/changeRole', methods= ["POST"])
def changeRole():
    result = guestUser()
    if(result == "GuestUser"):
        return result
    
    selectedRole = request.form["selectedRole"]
    session["role"] = selectedRole
    return session["username"] + session["role"]