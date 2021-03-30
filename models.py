import sqlite3
from datetime import datetime
from sqlite3.dbapi2 import Error
from utils import compare_time

# TODO: add logs for everything, to make life easier

DB_NAME = "festemberHunt21.db"

QUIZ_COMPLETED_TOAST = """You have already completed the hunt
    ||Thank you for helping us recover the stolen trophy.
    ||Follow our inductions handle - @festember_inductions on Instagram!
    ||https://instagram.com/festember_inductions 
    ||To learn more about the fest, visit our Instagram page @festember.
    ||https://instagram.com/festember"""

START_QUIZ_BEFORE_ASKING_FOR_CLUES_AND_HINTS_TOAST = (
    "Start Quiz with a `$hello` before asking for clue or hint! :)"
)

VIEW_CLUE_BEFORE_VIEWING_HINT_TOAST = "View the Clue before trying to view a hint!"

VIEWED_ALL_THE_HINTS_TOAST = "You have viewed all hints for this stage!"

HINT_AFTER_CLUE_COUNTDOWN = [15, 20, 0]
ATTEMPT_INTERVAL = [0.5, 0.25, 0]

CANNOT_VIEW_HINT_JUST_YET_TOAST = "Wait for some time before viewing hint!"
ATTEMPT_COOLDOWN_TOAST = "You have to wait some time before attempting again!"

START_QUIZ_BEFORE_ANSWERING_TOAST = "Start the quiz before trying to answer!"
VIEW_CLUE_BEFORE_ANSWERING_TOAST = "View clue before trying to answer!"
WRONG_ANS_TOAST = "Unfortunately, you have entered the wrong answer, please try again."
CORRECT_ANS_TOAST = "Congratulations, that is the correct answer."

REMIND_PLAYER_TO_VIEW_HINTS_TOAST = (
    "If you are having trouble getting the answer, always view hints!"
)
ATTEMPTS_BEFORE_VIEW_HINTS_TOAST = 5


class Database:
    """ Used to do crud operations on the db"""

    def __init__(self):
        self.conn, self.cursor = self.init_db()
        self.total_clues = self.get_total_clues()

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
                ) VALUES (?,?, -1, 0, null, null, 0, 0, null)"
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

    def answer_question(self, username, ans_is_correct, data):
        """sets the user's date, when a hunt is attempted"""
        if ans_is_correct:
            # de-structure
            (last_solved,) = data
            print("LAST SOLVED :", last_solved)
            query = "UPDATE users SET \
                last_solved=:last_solved,\
                last_solved_time=:last_solved_time,\
                last_attempted_time=NULL,\
                attempts=0,\
                hints_used=0,\
                last_hint_used_time=NULL WHERE name=:username"
            self.cursor.execute(
                query,
                {
                    "last_solved": last_solved,
                    "last_solved_time": datetime.now().timestamp(),
                    "username": username,
                },
            )
            return self.conn.commit()
        else:
            (attempts,) = data
            query = "UPDATE users SET \
                last_attempted_time=:last_attempted_time,\
                attempts=:attempts\
                WHERE name=:username"
            self.cursor.execute(
                query,
                {
                    "attempts": attempts,
                    "last_attempted_time": datetime.now().timestamp(),
                    "username": username,
                },
            )
            return self.conn.commit()

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

    def get_total_clues(self):
        """Finds the number of clues"""
        self.cursor.execute("SELECT COUNT(*) FROM clues")
        n = self.cursor.fetchone()
        return n[0]

    def get_single_clue(self, username):
        """Gets the user's current clue, has seen clue, hints_used, attempts"""
        user = self.find_user(username)
        query = "SELECT * FROM clues WHERE clue_id=:clueId"
        print(user)
        if user[3] == -1:
            # user is yet to start the quiz, ask him to say hello
            return (None,) * 4
        elif user[3] == 50 or user[3] == user[4] == self.total_clues:
            # user has finished the quiz,
            return (50,) + (None,) * 3
        self.cursor.execute(query, {"clueId": user[3]})
        clue = self.cursor.fetchone()

        # if the clue is not found, set clue to be a dummy clue
        if clue == None:
            clue = (0,) * 5

        # is user[3] == user[4] => he has not viewed the clue
        return clue, user[3] == user[4], user[8], user[7]

    def update_current_clue(self, username, current_clue):
        """Updates the current clue and last hint used time of the user"""
        n = self.total_clues
        if current_clue > n:
            # user has finished the quiz
            current_clue = 50  # setting clue to random no

        query = "UPDATE users SET current_clue = ?, last_hint_used_time = ? \
            WHERE name =?"
        self.cursor.execute(query, (current_clue, datetime.now().timestamp(), username))
        self.conn.commit()
        return self.get_single_clue(username)

    def update_hint_and_last_hint_used_time(self, username, new_hint):
        """Updates the hints_used and last_hint_used_time of a user"""
        query = (
            "UPDATE users SET last_hint_used_time = ?, hints_used = ? WHERE name = ?"
        )
        self.cursor.execute(query, (datetime.now().timestamp(), new_hint, username))
        return self.conn.commit()

    # ~~~~~~~ ACTUAL METHODS ~~~~~~~~~~~

    def start_hunt(self, username):
        """Returns a if the user is starting the hunt or not"""
        clue, _, _, _ = self.get_single_clue(username)
        if clue == None:
            print(username, "has started the hunt")
            self.update_current_clue(username, 0)
            return 0
        if clue == 50:
            return 2
        return 1

    def get_clue(self, username):
        """get the clue for the current question from the database,
        and returns the clue as a string"""
        # find the user
        clue, first_time, _, _ = self.get_single_clue(username)
        print("The clue is :", clue)
        if clue == None:
            return START_QUIZ_BEFORE_ASKING_FOR_CLUES_AND_HINTS_TOAST
        if clue == 50:
            return QUIZ_COMPLETED_TOAST
        if first_time:
            print("first time viewing the clue")
            clue, _, _, _ = self.update_current_clue(username, clue[0] + 1)
            if clue == 50:
                return QUIZ_COMPLETED_TOAST
            return "**Story : **||" + clue[3] + "||**Clue :  **||" + clue[1]
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
        if clue == 50:
            return QUIZ_COMPLETED_TOAST
        if first_time:
            return VIEW_CLUE_BEFORE_VIEWING_HINT_TOAST

        # find all hints for the given clue
        self.cursor.execute("SELECT * FROM hints WHERE clue_id=?", (clue[0],))
        hints = self.cursor.fetchall()
        if hints_used >= len(hints):
            return VIEWED_ALL_THE_HINTS_TOAST

        can_view_hint, time_left = compare_time(
            last_hint_used_time, HINT_AFTER_CLUE_COUNTDOWN[hints_used]
        )
        if can_view_hint:
            self.update_hint_and_last_hint_used_time(username, hints_used + 1)
            return "**Hint {} :**||".format(hints_used + 1) + hints[hints_used][3]
        else:
            return (
                CANNOT_VIEW_HINT_JUST_YET_TOAST
                + "||"
                + "Wait for {} before viewing the hint".format(time_left)
            )

    def check_ans(self, username, answer):
        """checks if the ans given by the user is correct,
        will return correct_toast/ wrong_toast appropriately"""
        clue, clue_not_viewed, hints_used, attempts = self.get_single_clue(username)
        (
            _,
            last_solved_time,
            last_attempted_time,
            last_hint_used_time,
        ) = self.get_user_time_stamps(username)
        # find the user
        if clue == None:
            return START_QUIZ_BEFORE_ANSWERING_TOAST
        if clue == 50:
            return QUIZ_COMPLETED_TOAST
        if clue_not_viewed:
            return VIEW_CLUE_BEFORE_ANSWERING_TOAST
        # the user has started the quiz, viewed the clue
        # now check if the user can attempt to ans

        # correct ans => reset attempts, last_attempt_time, hint_used, las_solved_time
        if last_attempted_time == None:
            # first time attempting this clue
            # no checks,directly check the answer
            if answer == clue[2]:
                self.answer_question(username, True, (clue[0],))
                return (
                    CORRECT_ANS_TOAST
                    + "||**Story Continues :**||"
                    + clue[4]
                    + "||Enter `$clue` to view the next clue."
                )
            else:
                # inc attempt, set attempt_time
                if (attempts + 1) >= ATTEMPTS_BEFORE_VIEW_HINTS_TOAST:
                    self.answer_question(username, False, (0,))
                    return WRONG_ANS_TOAST + "||" + REMIND_PLAYER_TO_VIEW_HINTS_TOAST
                else:
                    self.answer_question(username, False, (attempts + 1,))
                    return WRONG_ANS_TOAST
        can_view_clue1, time_left = compare_time(
            last_attempted_time, ATTEMPT_INTERVAL[hints_used]
        )
        # can_view_clue2, time_left2 = compare_time(
        #     last_hint_used_time, HINT_AFTER_CLUE_COUNTDOWN[hints_used]
        # )

        # # since, user has to wait for more time after viewing hint, tim_left2 > time_left
        # if can_view_clue2:
        #     time_left = time_left2
        if can_view_clue1:
            if answer == clue[2]:
                self.answer_question(username, True, (clue[0],))
                return (
                    CORRECT_ANS_TOAST
                    + "||**Story Continues :**||"
                    + clue[4]
                    + "||Enter `$clue` to view the next clue."
                )
            else:
                # inc attempt, set attempt_time
                if (attempts + 1) >= ATTEMPTS_BEFORE_VIEW_HINTS_TOAST:
                    self.answer_question(username, False, (0,))
                    return WRONG_ANS_TOAST + "||" + REMIND_PLAYER_TO_VIEW_HINTS_TOAST
                else:
                    self.answer_question(username, False, (attempts + 1,))
                    return WRONG_ANS_TOAST
        else:
            return (
                ATTEMPT_COOLDOWN_TOAST
                + "||"
                + "Wait for {} before answering the question".format(time_left)
            )

    def get_leaderboard(self):
        self.cursor.execute(
            "SELECT name, last_solved FROM users ORDER BY last_solved desc, last_solved_time asc LIMIT 50"
        )
        res = self.cursor.fetchall()
        # print("res", res)
        string = ""
        string += "```\n"
        string += "{:<10}  {:<20} {:<8}\n".format("Position", "Username", "Q. Solved")
        string += "__________________________________________\n"
        for pos, value in enumerate(res[:25]):
            if len(value[0]) <= 20:
                string += "{:<10} {:<20}  {:<8}\n".format(pos + 1, value[0], value[1])
            else:
                string += "{:<10} {:<20}  {:<8}\n".format(
                    pos + 1, value[0][:16] + "...", value[1]
                )
        string += "```||"
        string += "```\n"
        for pos, value in enumerate(res[25:]):
            if len(value[0]) <= 20:
                string += "{:<10} {:<20}  {:<8}\n".format(pos + 1, value[0], value[1])
            else:
                string += "{:<10} {:<20}  {:<8}\n".format(
                    pos + 1, value[0][:16] + "...", value[1]
                )
        string += "```"
        # print(string)
        return string
