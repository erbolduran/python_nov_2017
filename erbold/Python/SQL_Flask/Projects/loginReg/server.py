from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re


app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app,'users')
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[A-Z][-a-zA-Z]+$')

app.secret_key = 'yank'


def countLetters(word):
    count = 0
    for c in word:
        count += 1
    return count

@app.route('/')
def index():

	return render_template('index.html')

@app.route('/process', methods=['POST'])
def create():

	errors = 0
	session['fname'] = request.form['fname']
	session['lname'] = request.form['lname']
	session['email'] = request.form['email']
	session['password'] = request.form['password']
	session['password2'] = request.form['password2']

	print session['password']

	if session['fname'] == '' or session['lname'] == '' or session['email'] == '' or session['password'] == ''or session['password2'] == '':
		flash('Submit Error')
		errors += 1	
	
	if not email_regex.match(session['email']):
		flash("Invalid Email Address!")	
		errors += 1

	if not name_regex.match(session['fname']) or not name_regex.match(session['lname']):
		flash('Letters Only Ninja!')
		errors += 1

	if session['password'] != session['password2']:
		flash('Password does not match')	
		errors += 1

	First_name = countLetters(session['fname'])
	print First_name
	if First_name < 2:
		flash('length error')
		errors += 1

	Last_name = countLetters(session['lname'])
	print Last_name
	if Last_name < 2:
		flash('length error')
		errors += 1				

	password = countLetters(session['password'])
	print password
	if password < 8:
		flash('length error')
		errors += 1		

	if errors == 0:
		flash("Valid Registration")
		pw_hash = bcrypt.generate_password_hash(session['password'])
		query = "INSERT INTO userinfo (first_name, last_name, email, password, created_at, updated_at)VALUES(:first_name, :last_name, :email, :password, NOW(), NOW())"
		data = {
			'first_name': session['fname'],
			'last_name': session['lname'],
			'email': session['email'],		
			'password': pw_hash
		}
		mysql.query_db(query, data)
		return redirect('/results')
	return redirect('/')	

@app.route('/login', methods=['POST'])
def login():

    if request.form['email1'] and request.form['password3']:
        query = "SELECT * FROM userinfo WHERE email=:email"
        data = {
            'email': request.form['email1']
        }
        user = mysql.query_db(query, data)[0]
        print(user)
        if bcrypt.check_password_hash(user['password'], request.form['password3']):
            return render_template('/results.html')
    flash("Incorrect username or password")
    return redirect('/')

@app.route('/results')
def show_emails():
# 	email = session['email']
# 	query = "SELECT email, date_format(created_at, '%m:%d:%y %1:%i %p') as created_at FROM emails"
# 	emails = mysql.query_db(query)

	return render_template('results.html')

app.run(debug=True)