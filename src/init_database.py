import sqlite3 as sql
import sys
import os

if sys.argv[1] != "-y":
	print("This script will erase all data in the database. Re-run with the -y commandline argument to confirm")
	exit()

os.remove("app.db")

sqlConnection = sql.connect('app.db')
cursor = sqlConnection.cursor()

cursor.execute(
	"""CREATE TABLE user (
			id              BIGINT  NOT NULL,
			username        TEXT    NOT NULL,
			password_hash   BLOB    NOT NULL,
			salt            BLOB    NOT NULL,
			firstName       TEXT,
			lastName        TEXT,
			email           TEXT,
			address         TEXT,
			city            TEXT,
			state           TEXT,
			zipcode         varchar(5),
			PRIMARY KEY (id)
		);
	""")