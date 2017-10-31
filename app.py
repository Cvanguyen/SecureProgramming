from flask import Flask, render_template, request, session, flash
from flaskext.mysql import MySQL 
from datetime import timedelta
import hashlib, uuid, os, sys, ctypes, bcrypt
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

@app.route('/', methods=['POST','GET'])
@app.route('/index.html')
@app.route('/index', methods=['POST','GET'])
def login():
	if request.methods == 'POST':
		username = request.form['username']
		password = request.form['password']
		query = "select password from user where username = '"+username+"'"
		cursor.execute(query)
		if cursor.rowcount == 1:
			result = cursor.fetchall()
			for row in result:
				hashed = bcrypt.hashpw(password, row[0])

				if hashed == row[0]:
					return render_template('upload.html', username = username)
				else: 
					return render_template('login.html')
	else:
		return render_template('login.html')


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

		#hash password
		hashed_password = bycrypt.hashpw(password,bcrypt.gensalt())

		query = "insert into user (username,password) values ('"+username+"','"+hashed_password+"')"
		message = 'Account created successfully!'
		cursor.execute(query)
		db.commit()
		return render_template('index.html', message=message)
	else: 
		return render_template('register.html')

@app.route('/upload', methods=['POST','GET'])
def upload():
	if request.methods == 'POST':
		file = request.files['file']
		if not file:
			message='No file selected to be scanned!'
			return render_template('upload.html', message=message)
		file_name = file.filename
		file_content = file.read()
		file_size = len(file_content)
		if file_size > 3000000:
			message = 'File size exceeded 3MB! Please upload another file!'
			return render_template('upload.html', message=message)
		if file_size <= 0: 
			message = 'File is empty!'
			return render_template('upload.html', message=message)
		valid, file_type = file_extension_check(file_content)

		if not valid: 
			message = 'Invalid file type! Please upload C/C++, Python, Perl or PHP file'
			return render_template('upload.html', message=message)

		data_dir = "user_data/" + username
		if not os.path.exists(data_dir):
			os.makedirs(data_dir)

		code_file = open(os.path.join("user_data", username, file_name), 'w')
		code_file.write(file_content)
		code_file.close()

		flawfinder_output_filename = ""
		rats_output_filename = ""
		flawfinder_output_content = "n/a"
		rats_output_content = "n/a"


		if file_type == 'C source':
			flawfinder_output_filename = os.path.join("user_data", username, file_name) + "flawfinder.txt"
			rats_output_filename = os.path.join("user_data", username, file_name) + "rats.txt"
			flawfinder_system_query = "flawfinder " + os.path.join("user_data", username, file_name) + " > " + flawfinder_output_filename
			rats_system_query = "rats -w 3 " + os.path.join("user_data", username, file_name) + " > " + rats_output_filename

			flawfinder_output_content = ""
			rats_output_content = ""
			subprocess.Popen(flawfinder_system_query, shell=True)
			subprocess.Popen(rats_system_query, shell=True)
		else:
			rats_output_filename=os.path.join("user_data", username, file_name) + "rats.txt"
			rats_system_query = "rats -w 3" + os.path.join("user_data", username, file_name) + " > " + rats_output_filename
			rats_output_content=""
			subprocess.Popen(rats_system_query, shell=True)

		message = "Upload Successfully!"
		return render_template('index.html', message=message)
def file_extension_check(file_content):
	valid = False
	#check from buffer what is the extension
	ext_type = str(magic.from_buffer(file_content))
	file_type = ext_type.split(",")[0]
	if file_type == "C source" or file_type == "Python script" or file_type == "a /usr/bin/perl script" or file_type == "PHP script" or file_type == "HTML document":
		valid == True
	return valid, file_type

if __name__ == "__main__":
	app.run()