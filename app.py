from flask import Flask, render_template, request, session, flash
from flaskext.mysql import MySQL 
from datetime import timedelta
import hashlib, uuid, os, sys, re, ctypes
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
db = mysql.connect()
print "Connection Established!!"
cursor = db.cursor()

#create session 
#@app.before_request
#def make_session():
	#session stays valid for 5 minutes after the browser is closed
#	session.permanent = True;
#	app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/', methods=['GET'])
def main():
	return render_template('index.html')

@app.route('/register', methods=['POST','GET'])
def register(): 
		#client = None 
		#get username 
	if request.methods == 'POST':
		username = request.form['username']
		password = request.form['password']
			
		query = "select username from user where username='"+username+"'"
		cursor.execute(query)
		if cursor.rowcount <> 0:
			message='Username already exists!'
			return render_template('register.html', message=message)

			#get random salt to hash with the password
		salt = uuid.uuid4().hex
		hashed_password = hex_generator(password+salt)

		query = "insert into user (username,password) values ('"+username+"','"+hashed_password+"')"
		message = 'Account created successfully!'
		cursor.execute(query)
		db.commit()
		return render_template('index.html', message=message)
	else: 
		return render_template('register.html')
		
if __name__ == "__main__":
	app.run()