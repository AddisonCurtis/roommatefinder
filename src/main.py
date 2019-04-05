import os
import random
import sqlite3 as sql
import hashlib
import json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import CORS
import flask_login

app = Flask(__name__, template_folder=".")
app.secret_key = "placeholder key" # TODO: Load secret key from a config file that isn't stored in the repo
CORS(app)
sqlConnection = sql.connect('app.db', check_same_thread=False)
cursor = sqlConnection.cursor()
loginManager = flask_login.LoginManager(app)


## Static web pages
@app.route("/")
def staticMainPage():
	return redirect(url_for("staticIndexPage"))

@app.route("/index")
def staticIndexPage():
	return render_template("index.html")

@app.route("/signup")
def staticSignupPage():
	if flask_login.current_user.is_authenticated:
		return redirect(url_for("staticMainPage"))

	return render_template("signup.html")

@app.route("/login")
def staticLoginPage():
	if flask_login.current_user.is_authenticated:
		return redirect(url_for("staticMainPage"))

	return render_template("login.html")

@app.route("/map")
def staticMapPage():
	return render_template("map.html")

@app.route("/profile")
def staticProfilePage():
	return render_template("profile.html")

## User stuff
class User(flask_login.UserMixin):
	pass

@loginManager.user_loader
def userLoader(userId):
	userRow = cursor.execute("SELECT * FROM user WHERE id = ?")
	if userRow is none:
		return

	user = User()
	user.id = userId
	return user

@loginManager.request_loader
def requestLoader(req):
	email = req.form.get('email')
	if email is None:
		return None

	userRow = cursor.execute("SELECT id, password_hash, salt FROM user WHERE email = ?", email)
	if userRow is none:
		return None

	user = User()
	user.id = userRow["id"]

	passwordHash = hashlib.pbkdf2('sha256', req.form['password'].encode(), salt, 10000)

	user.is_authenticated = passwordHash == userRow["password_hash"]

	return user


## API endpoints
@app.route("/api/users")
def getUsers():
	cursor.execute("SELECT id, username, firstName, lastName, email, address, state, city, zipcode FROM user")
	return jsonify(cursor.fetchall())

@app.route("/api/signup", methods=["POST"])
def newUser():
	username = request.form["username"]
	plainPassword = request.form["password"]
	firstName = request.form["firstName"]
	lastName = request.form["lastName"]
	email = request.form.get("email")
	# TODO: Implement checks for structure and integrity (I.E. first/last name is present, email is valid)

	userId = random.getrandbits(64)
	salt = os.urandom(32);

	passwordHash = hashlib.pbkdf2('sha256', plainPassword.encode(), salt, 10000)

	cursor.execute("SELECT * FROM user WHERE username = ? OR email = ?", username, email)
	if cursor.fetchone() is not None:
		return status.HTTP_409_CONFLICT # TODO: Find a way to specify which field had an issue. In the response, maybe?

	cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			userId, username, passwordHash, salt, firstName, lastName,
			email, request.form["address"], request.form["city"],
			request.form["state"], request.form["zipcode"]
			)

	return status.HTTP_200_OK

@app.route("/api/login", methods=['POST'])
def login():
	if flask_login.current_user.is_authenticated:
		return status.HTTP_200_OK

	user = requestLoader(request)
	if user is not None:
		flask_login.login_user(user)
		return status.HTTP_200_OK

	return status.HTTP_400_BAD_REQUEST


if __name__ == '__main__':
	app.run()
