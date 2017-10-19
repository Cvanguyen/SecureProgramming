from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_mysql import MySQL 
from datetime import timedelta
import hashlib, uuid, os, sys, re
import ConfigParser
import subprocess 

mysql = MySQL() 
app = Flask(__name__)

#MySQL configuration 
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'SecureWebApp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#create session 
#@app.before_request
#def make_session():
	#session stays valid for 5 minutes after the browser is closed
#	session.permanent = True;
#	app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/', methods=['GET'])
def main():
	return render_template('index.html')

@app.route('/ShowRegister', methods=['GET'])
def ShowRegister():
		return render_template('register.html')

@app.route("/register", methods=['POST'])
def register(): 
	try:
		client = None 
		#get username 
		username = request.form['username']
		if username == "":
			flash("Username is needed!")
			return redirect(url_for('ShowRegister'), code=302)
		#check for username based on white list
		qualify = name_validation(username)
		if not qualify:
			flash("Invalid username! Username must have 4-15 characters with only alphabets and numbers") 
			return redirect(url_for('ShowRegister'), code=302)

		#get password 
		password = request.form['password']
		if password == "":
			flash("Password is needed!")
			return redirect(url_for('ShowRegister'), code=302)
		#check for password based on white list	
		qualify = password_validation(password)
		if not qualify:
			flash("Password must have 4-15 characters with special characters ! @ # $ % ^ & * ( )")
			return redirect(url_for('ShowRegister'), code=302)

		#get random salt to hash with the password
		salt = uuid.uuid4().hex
		hashed_password = hex_generator(password+salt)

		if username and password: 
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('check_user',(username,hashed_password))
			data = cursor.fetchall()

			if len(data) is 0: 
				conn.commit()
				flash("User created successfully!")
				return json.dumps({'message':'User created successfully !'})
				#return redirect(url_for('main'),code=302)
			else:
				flash("Error!")
				json.dumps({'error':str(data[0])})
				#return redirect(url_for('main'),code=302)
	except:
		flash("Error has occured!") 
		return redirect(url_for('main'),code=302)
	finally: 
		#erasing password 
		password = ""
		password += ""
		cursor.close()
		conn.close()

if __name__ == "__main__":
	app.run()