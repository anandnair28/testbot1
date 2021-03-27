import sqlite3
import datetime
from sqlite3.dbapi2 import Error

# def init_db():
#   conn = sqlite3.connect("festemberHunt21")
#   return con


DB_NAME = "festemberHunt21.db"


class Database:
    """ Used to do crud operations on the db"""

    def __init__(self):
        self.conn, self.cursor = self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name in ('users', 'score', 'clues');"
            )
            r = c.fetchall()
            # print(r)
            if len(r) == 3:
                print("Tables already exist, setting up connection with db!")
                return conn, c
            print("Tables don't exist, creating them")
            c.execute(
                """CREATE TABLE IF NOT EXISTS users ( 
				user_id integer PRIMARY KEY,
				name text NOT NULL, 
				time_joined timestamp,
				clue integer);"""
            )
            print("Created users table")
            c.execute(
                """CREATE TABLE IF NOT EXISTS clues (
                clue_id integer PRIMARY KEY,
                clue text,
                clue_time datetime,
                hint text,
                hint_time datetime,
                correct_toast text,
                wrong_toast text
            );"""
            )
            print("Created clues table")
            c.execute(
                """CREATE TABLE IF NOT EXISTS score (
				score_id integer PRIMARY KEY,
                user_id integer NOT NULL,
				score integer,
				FOREIGN KEY (user_id) REFERENCES users (id)
				);"""
            )
            print("created score table")
            print("Tables have been created, connecting to db")
            conn.commit()
            return conn, c
        except Exception as e:
            print("couldn't create db, {}".format(str(e)))
            return "error", 400

    def add_user(self, name):
        """adds user to db and"""
        try:
            print("Inserting a person with the username, ", name)
            time = datetime.datetime.now()
            query = "INSERT INTO users(name, time_joined, clue) VALUES(?,?,?)"
            self.cursor.execute(query, (name, datetime.datetime.timestamp(time), 1))
            self.conn.commit()
            print("Created a user with the id:", self.cursor.lastrowid)
            self.cursor.execute(
                "SELECT * FROM users WHERE user_id=?", (self.cursor.lastrowid,)
            )
            result = self.cursor.fetchone()
            print("created a user :", result)
            return result
        except Exception as e:
            print("couldn't create a row in the db, {}".format(str(e)))

    def find_user(self, name):
        """Returns the user item for the given username,
        if such a user doesn't exist creates one"""
        query = "SELECT * FROM users WHERE name=:name"
        self.cursor.execute(query, {"name": name})
        result = self.cursor.fetchone()
        print("Got the result when trying to find a user:,", result)
        if result == None:
            print("Such a user doesn't exist")
            return self.add_user(name)
        return result
