import sqlite3 as sql
from flask import Flask, request, render_template, redirect, url_for
import json
from flask_cors import CORS

app = Flask(__name__, template_folder=".")
CORS(app)
sqlConnection = sql.connect('app.db')
cursor = sqlConnection.cursor()

## Static web pages
@app.route("/")
def staticMainPage():
	return redirect(url_for("staticIndexPage"))

@app.route("/index")
def staticIndexPage():
	return render_template("index.html")

@app.route("/login")
def staticLoginPage():
	return render_template("login.html")

@app.route("/map")
def staticMapPage():
	return render_template("map.html")

@app.route("/profile")
def staticProfilePage():
	return render_template("profile.html")


## API endpoints
@app.route("/api/users", methods=["GET"])
def getUsers():
	return cursor.execute("SELECT name FROM users")


if __name__ == '__main__':
	app.run()
