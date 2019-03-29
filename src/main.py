import sqlite3 as sql
from flask import Flask, request, render_template, redirect, url_for, jsonify
import json
from flask_cors import CORS
import hashlib
import os
import random
from flask_login import LoginManager, current_user

app = Flask(__name__, template_folder=".")
CORS(app)
sqlConnection = sql.connect('app.db', check_same_thread=False)
cursor = sqlConnection.cursor()
loginManager = LoginManager(app)

#class User(UserMixin):


## Static web pages
@app.route("/")
def staticMainPage():
	return redirect(url_for("staticIndexPage"))

@app.route("/index")
def staticIndexPage():
	return render_template("index.html")

@app.route("/signup")
def staticLoginPage():
	if current_user.is_authenticated:
		return redirect(url_for("staticMainPage"))

	return render_template("signup.html")

@app.route("/map")
def staticMapPage():
	return render_template("map.html")

@app.route("/profile")
def staticProfilePage():
	return render_template("profile.html")


## API endpoints
@app.route("/api/users")
def getUsers():
	cursor.execute("SELECT id, username, firstName, lastName, email, address, state, city, zipcode FROM user")
	return jsonify(cursor.fetchall())

@app.route("/api/user", methods=["POST"])
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

	cursor.execute("SELECT id FROM user WHERE username = ? OR email = ?", username, email)
	if cursor.fetchone() is not None:
		return status.HTTP_409_CONFLICT # TODO: Find a way to specify which field had an issue. In the response, maybe?

	cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			userId, username, passwordHash, salt, firstName, lastName,
			email, request.form["address"], request.form["city"],
			request.form["state"], request.form["zipcode"]
			)

	return status.HTTP_200_OK

@app.route("/api/login")
def login():
	if current_user.is_authenticated:
		content = {"Location": f"{request.url_root}login"}
		return content, status.HTTP_303_SEE_OTHER



if __name__ == '__main__':
	app.run()
