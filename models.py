import sqlite3
from datetime import datetime
from sqlite3.dbapi2 import Error
from utils import compare_time

# TODO: BUG CHECK IF USER VIEWED CLUE FOR 1ST QUESTION
# TODO: ADD FEATURE TO SEND WAIT TIME BEFORE VIEWING A CLUE

# TODO: add logs for everything, to make life easier

DB_NAME = "festemberHunt21.db"

QUIZ_COMPLETED_TOAST = "You have already completed the hunt. chill"

START_QUIZ_BEFORE_ASKING_FOR_CLUES_AND_HINTS_TOAST = (
    "start the quiz before asking for clues and answers"
)

VIEW_CLUE_BEFORE_VIEWING_HINT_TOAST = "view clue before viewing hint"

VIEWED_ALL_THE_HINTS_TOAST = "you have viewed all the hints"

HINT_AFTER_CLUE_COUNTDOWN = 30

CANNOT_VIEW_HINT_JUST_YET_TOAST = "wait for sometime before viewing the clue"


class Database:
    """ Used to do crud operations on the db"""

    def __init__(self):
        self.conn, self.cursor = self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name in ('users', 'hints', 'clues');"
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
                current_clue integer NOT NULL,
                last_solved integer NOT NULL,
                last_solved_time timestamp,
                last_attempted_time timestamp,
                attempts integer NOT NULL,
                hints_used integer NOT NULL,
                last_hint_used_time timestamp
				);"""
            )
            print("Created users table")
            c.execute(
                """CREATE TABLE IF NOT EXISTS clues (
                clue_id integer PRIMARY KEY,
                clue text,
                answer text,
                story_start text,
                story_continue text
            );"""
            )
            print("Created clues table")
            c.execute(
                """CREATE TABLE IF NOT EXISTS  hints(
				hint_id integer PRIMARY KEY,
                clue_id integer NOT NULL,
				hint_no integer,
                hint text,
				FOREIGN KEY (clue_id) REFERENCES clues (clue_id)
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
            query = "INSERT INTO users( \
                name, time_joined, current_clue, last_solved, last_solved_time, \
                last_attempted_time, attempts,hints_used, last_hint_used_time\
                ) VALUES (?,?,0, 0, null, null, 0, 0, null)"
            self.cursor.execute(query, (name, datetime.now().timestamp()))
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

    def get_user_time_stamps(self, username):
        """Returns all the time stamps of the user
        (time_joined, last_solved_time, last_attempted_time, last_hint_used_time)"""
        user = self.find_user(username)
        return user[2], user[5], user[6], user[9]

    def add_clues(self, clue):
        """add clues to the db,clue object must be of the type
            clue : {
            "clue": string,
            "answer": string,
            "story_start": string,
            "story_continue": string,
            "hints": [
                "hints"
            ]
        },"""
        query = "INSERT INTO clues(clue, answer, story_start, story_continue) \
        VALUES (:clue, :answer, :story_start, :story_continue)"
        self.cursor.execute(query, clue)
        self.conn.commit()
        print("Added a clue to the db with the row no, ", self.cursor.lastrowid)
        clue_id = self.cursor.lastrowid
        print("Adding hints for the clues")
        for hint_no, hint in enumerate(clue["hints"]):
            self.add_hints(hint, hint_no + 1, clue_id)

    def add_hints(self, hint, hint_no, clue_id):
        """Adds hints to the database for the given clue"""
        query = "INSERT INTO hints(clue_id, hint_no, hint) \
            VALUES(?, ?, ?)"
        self.cursor.execute(query, (clue_id, hint_no, hint))
        self.conn.commit()
        return

    def get_single_clue(self, username):
        """Gets the user's current clue, has seen clue, hints_used, attempts"""
        user = self.find_user(username)
        query = "SELECT * FROM clues WHERE clue_id=:clueId"
        print(user)
        if user[3] == 0:
            # user is yet to start the quiz, ask him to say hello
            return (None,) * 4
        elif user[3] == 50:
            # user has finished the quiz,
            return (-1,) + (None,) * 3
        self.cursor.execute(query, {"clueId": user[3]})
        clue = self.cursor.fetchone()

        # is user[3] == user[4] => he has not viewed the clue
        return clue, user[3] == user[4], user[8], user[7]

    def update_current_clue(self, username, current_clue):
        """Updates the current clue of the user"""
        self.cursor.execute("SELECT COUNT(*) FROM clues")
        n = self.cursor.fetchone()
        print("No of clues is :", n[0])
        if current_clue > n[0]:
            # user has finished the quiz
            current_clue = 50  # setting clue to random no

        query = "UPDATE users SET current_clue = ? WHERE name =?"
        self.cursor.execute(query, (current_clue, username))
        self.conn.commit()

    def update_hint_and_last_hint_used_time(self, username, new_hint):
        """Updates the hints_used and last_hint_used_time of a user"""
        query = (
            "UPDATE users SET last_hint_used_time = ?, hints_used = ? WHERE name = ?"
        )
        self.cursor.execute(query, (datetime.now().timestamp(), new_hint, username))
        return self.conn.commit()

    def start_hunt(self, username):
        """Returns a if the user is starting the hunt or not"""
        clue, _, _, _ = self.get_single_clue(username)
        if clue == None:
            print(username, "has started the hunt")
            self.update_current_clue(username, 1)
            return True
        return False

    def get_clue(self, username):
        """get the clue for the current question from the database,
        and returns the clue as a string"""
        # find the user
        clue, first_time, _, _ = self.get_single_clue(username)
        if clue == None:
            return START_QUIZ_BEFORE_ASKING_FOR_CLUES_AND_HINTS_TOAST
        if clue == -1:
            return QUIZ_COMPLETED_TOAST
        if first_time or clue[0] == 1:
            print("first time viewing the clue")
            self.update_current_clue(username, clue[0])
            return clue[3] + "||" + clue[1]
        else:
            print("viewing the clue again")
            return clue[1]

    def get_hint(self, username):
        """get the hint for the current question from the database,
        and returns the hint as a string"""
        # find the user
        clue, first_time, hints_used, _ = self.get_single_clue(username)
        (
            time_joined,
            last_solved_time,
            last_attempted_time,
            last_hint_used_time,
        ) = self.get_user_time_stamps(username)
        if clue == None:
            return START_QUIZ_BEFORE_ASKING_FOR_CLUES_AND_HINTS_TOAST
        if clue == -1:
            return QUIZ_COMPLETED_TOAST
        if first_time:
            return VIEW_CLUE_BEFORE_VIEWING_HINT_TOAST

        # find all hints for the given clue
        self.cursor.execute("SELECT * FROM hints WHERE clue_id=?", (clue[0],))
        hints = self.cursor.fetchall()
        if hints_used >= len(hints):
            return VIEWED_ALL_THE_HINTS_TOAST

        if hints_used == 0:
            # user wants to see the first hint
            if clue[0] == 1:
                # user is currently in first clue so, compare with time_joined,
                # .   to verify if he can view the clue
                if compare_time(time_joined, HINT_AFTER_CLUE_COUNTDOWN):
                    self.update_hint_and_last_hint_used_time(username, 1)
                    return hints[0][3]
                else:
                    return CANNOT_VIEW_HINT_JUST_YET_TOAST
            else:
                # user is viewing >1 clue,
                # . so compare with the last_solved_time
                if compare_time(last_solved_time, HINT_AFTER_CLUE_COUNTDOWN):
                    self.update_hint_and_last_hint_used_time(username, hints_used + 1)
                    return hints[hints_used][3]
                else:
                    return CANNOT_VIEW_HINT_JUST_YET_TOAST
        else:
            # user has already viewed all a hint, so compare with last_hint_time
            if compare_time(last_hint_used_time, HINT_AFTER_CLUE_COUNTDOWN):
                self.update_hint_and_last_hint_used_time(username, hints_used + 1)
                return hints[hints_used][3]
            else:
                return CANNOT_VIEW_HINT_JUST_YET_TOAST

    def check_ans(self, username, answer):
        """checks if the ans given by the user is correct,
        will return correct_toast/ wrong_toast appropriately"""
        # find the user
        clue = self.get_single_clue(username)
        if clue == None:
            return QUIZ_COMPLETED_TOAST
        clue_time = datetime.fromtimestamp(clue[2])
        current_time = datetime.now()
        if current_time > clue_time:
            # user is answering question after the question is out
            if answer == clue[7]:
                self.update_user_current_clue(username, clue[0] + 1)
                return clue[5]
            else:
                return clue[6]
        else:
            # user answering question before the question is out
            return "too fast, wait for sometime"

    def update_user_current_clue(self, username, clue_no):
        """updates the question number for the given username to the given number"""
        print("Updating the user's current clue to", clue_no)
        # checking if the user has completed the quiz,
        # if yes, we set the clue to 0 in users table
        self.cursor.execute("SELECT COUNT(*) FROM clues")
        n = self.cursor.fetchone()
        if clue_no > n[0]:
            clue_no = 0
        query = "UPDATE users SET clue = ? WHERE name =?"
        self.cursor.execute(query, (clue_no, username))
