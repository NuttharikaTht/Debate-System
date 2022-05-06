import Voting.user as user
from flask import Flask,flash, request, render_template, redirect, session, url_for, Blueprint
import mysql.connector
from werkzeug.security import check_password_hash

app = Flask(__name__)

#ทำ blueprints เพื่อเอาไปรันบน route หลักที่ app.py
debate_blueprint = Blueprint('debate_blueprint', __name__, template_folder="templates", static_folder='static', static_url_path='/static')

@debate_blueprint.route('/home')
def home():
	return render_template('Home.html')

@debate_blueprint.route('/about')
def about():
	return render_template('About.html')

@debate_blueprint.route("/debateRoom")
def debateRoom():
    mydb = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
    )
    #fetch and select data from database
    list = []
    mycursor = mydb.cursor()
    sql_statement = "SELECT * FROM book_room"
    mycursor.execute(sql_statement)
    output = mycursor.fetchall()
    for row in output:
        list.append({'roomID' : row[0], 
					'date' : str(row[1]), 
					'time' : str(row[2]), 
					'Title' : row[3], 
					'Proposition' : row[4], 
					'Opposition' : row[5],
					'link' : row[6]
			
		})
        #test fetch data and write json file
    '''with open('result.json', 'w') as outfile:
        json.dump(list, outfile, indent=4)'''
    return render_template('Debate_room.html', list = list)

#logout and close session and redirest to page login
@debate_blueprint.route('/logout',methods=['POST'])
def logout():
	session.pop('User', None)
	return redirect('/')

#press get start from home and direct to Debate_room and show data from database
@debate_blueprint.route('/getstart')
def debateroom():
    #fetch and select data from database
    mydb = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
    )
    list = []
    mycursor = mydb.cursor()
    sql_statement = "SELECT * FROM book_room"
    mycursor.execute(sql_statement)
    output = mycursor.fetchall()
    for row in output:
        list.append({'roomID' : row[0], 
                     'date' : str(row[1]), 
                     'time' : str(row[2]), 
                     'Title' : row[3], 
                     'Proposition' : row[4], 
                     'Opposition' : row[5],
                     'link' : row[6],
                     'zoomPass' : row[7]

        })
        #test fetch data and write json file
    '''with open('result.json', 'w') as outfile:
        json.dump(list, outfile, indent=4)'''
    return render_template('Debate_room.html', list = list)

#ให้แสดง path ตาม roomID 
@debate_blueprint.route('/roomid/<roomID>',methods=["GET","POST"])
def vv(roomID):
    mydb = mysql.connector.connect(
        host = "us-cdbr-east-04.cleardb.com",
        user = "b65b46c196f747",
        passwd = "dcc34691",
        database = "heroku_8bbbdf5cf23f9c0"
    )
    data = []
    word = request.form["name"]
    #test data from html ดูว่ากดเลือกชื่อห้องแล้วจะได้อะไรกลับมาเลยลองเอาค่ามาเขียนในไฟล์ .txt
    '''with open('input.txt', 'w') as f:
       f.write(word)'''
    mycursor = mydb.cursor()
    
    mycursor.execute("select * from book_room where roomID='"+roomID+"'")
    #fetch data ออกมาแล้วส่งค่าไปยัง vote.html
    result = mycursor.fetchall()
    for row in result:
        data.append({'roomID' : row[0], 
                     'date' : str(row[1]), 
                     'time' : str(row[2]), 
                     'Title' : row[3], 
                     'Proposition' : row[4], 
                     'Opposition' : row[5],
                     'link' : row[6],
                     'zoomPass' : row[7]

        })
    return render_template('joinRoom.html', data=data) 