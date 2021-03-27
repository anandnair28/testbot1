import json
from models import Database


def seed():
    data_file = open("data.json")
    data = json.load(data_file)
    print(len(data))
    db = Database()
    db.cursor.execute("SELECT COUNT(*) FROM clues")
    n = db.cursor.fetchone()
    if n[0] == len(data):
        return print("the database has already been seeded")

    print("need to seed db")
    print(data[0])
    for d in data:
        db.add_clues(d)
    print("added all the clues to the db")
    db.cursor.execute("SELECT * FROM clues")
    res = db.cursor.fetchall()
    print("the added data is :", res)


if __name__ == "__main__":
    seed()
