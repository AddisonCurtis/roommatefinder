import os
import random
import sqlite3
import hashlib
import json

from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import CORS
import flask_login

app = Flask(__name__)
app.secret_key = "placeholder key" # TODO: Load secret key from a config file that isn"t stored in the repo
CORS(app)
sqlConnection = sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)
cursor = sqlConnection.cursor()
loginManager = flask_login.LoginManager()
loginManager.init_app(app)

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
@flask_login.login_required
def staticProfilePage():
	return render_template("profile.html")

@app.route("/all_listings")
def staticAllListingsPage():
	return render_template("listings.html")
	
@app.route("/createlisting")
def staticListingsPage():
	return render_template("create_listing.html")

## User stuff
class User(flask_login.UserMixin):
	def __init__(self, userId = None):
		self.userId = userId

	
	def get_id(self):
		cursor.execute("SELECT * FROM user WHERE id = ?", (self.userId,))
		userRow = cursor.fetchone()
		if userRow is None:
			return None

		return str(userRow[0])
		

@loginManager.user_loader
def userLoader(userId):
	userRow = cursor.execute("SELECT * FROM user WHERE id = ?", (userId,))
	if userRow is None:
		return None

	return User(userId)

@loginManager.request_loader
def requestLoader(req):
	email = req.form.get("email")
	if email is None:
		return None

	cursor.execute("SELECT id, password_hash, salt FROM user WHERE email = ?", (email,))
	userRow = cursor.fetchone()
	if userRow is None:
		return None

	user = User(userRow[0])

	passwordHash = hashlib.pbkdf2_hmac("sha256", req.form["password"].encode(), userRow[2], 10000)

	if passwordHash != userRow[1]:
		return None

	return user


## API endpoints
@app.route("/api/users")
def getUsers():
	cursor.execute("SELECT id, firstName, lastName, email, address, state, city, zipcode FROM user")
	return jsonify(cursor.fetchall())

@app.route("/api/signup", methods=["POST"])
def newUser():
	plainPassword = request.form["password"]
	firstName = request.form["firstName"]
	lastName = request.form["lastName"]
	email = request.form.get("email")
	# TODO: Implement checks for structure and integrity (I.E. first/last name is present, email is valid)

	userId = random.getrandbits(63)
	salt = os.urandom(32);

	passwordHash = hashlib.pbkdf2_hmac("sha256", plainPassword.encode(), salt, 10000)

	cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
	if cursor.fetchone() is not None:
		return json.dumps({"success": False}), 409

	cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(userId , passwordHash, salt, firstName, lastName,
			email, request.form["address"], request.form["city"],
			request.form["state"], request.form["zipcode"])
			)

	flask_login.login_user(User(userId), remember = True)

	return json.dumps({"success": True}), 200

@app.route("/api/login", methods=["POST"])
def login():
	#if not flask_login.current_user.is_anonymous:
	#	return json.dumps({"success": True}), 200

	user = requestLoader(request)
	if user is None:
		return json.dumps({"success": False}), 400

	flask_login.login_user(user, remember = True)
	return json.dumps({"success": True}), 200

@app.route("/api/logout", methods=["POST"])
@flask_login.login_required
def logout():
	flask_login.logout_user()
	return json.dumps({"success": True}), 200

@app.route("/api/createlisting", methods=["POST"])
@flask_login.login_required
def createListing():

	cursor.execute("INSERT INTO listing VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(random.getrandbits(63) , flask_login.current_user.get_id(), request.form["name"], request.form["description"], request.form["price"],
			request.form["bedcount"], request.form["bathcount"], request.form["address"],
			request.form["city"], request.form["state"], request.form["zipcode"],
			request.form["smoking"], request.form["internet"])
			)
	return json.dumps({"success": True}), 200

if __name__ == "__main__":
	app.run()
