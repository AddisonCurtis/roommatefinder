import sqlite3 as sql
import sys
import os

if len(sys.argv) != 2:
	print("This script will erase all data in the database. Re-run with the -y commandline argument to confirm")
	exit()

if sys.argv[1] != "-y":
	print("This script will erase all data in the database. Re-run with the -y commandline argument to confirm")
	exit()

os.remove("app.db")

sqlConnection = sql.connect('app.db')
cursor = sqlConnection.cursor()

cursor.execute(
	"""CREATE TABLE user (
			id              BIGINT  NOT NULL,
			password_hash   BLOB    NOT NULL,
			salt            BLOB    NOT NULL,
			firstName       TEXT,
			lastName        TEXT,
			email           TEXT,
			address         TEXT,
			city            TEXT,
			state           TEXT,
			zipcode         varchar(10),
			PRIMARY KEY (id)
		);
	""")
cursor.execute(
	"""CREATE TABLE listing (
			id              BIGINT  NOT NULL,
			listname        TEXT    NOT NULL,
			description   	TEXT    NOT NULL,
			price			INT		NOT NULL,
			bedcount   	    INT		NOT NULL,
			bathcount       INT		NOT NULL,
			smoking        	BOOL	NOT NULL,
			internet        BOOL	NOT NULL,
			address         TEXT,
			city            TEXT,
			state           TEXT,
			zipcode         varchar(5),
			PRIMARY KEY (id)
		);
	""")
