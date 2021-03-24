import sqlite3


def init_db():
  conn = sqlite3.connect("test.db")
  return conn

conn = sqlite3.connect("test.db")

def hello_world():
  return print("Hello world 2.0")
  

print("Created a database successfully")

conn.execute(
    """CREATE TABLE USER
  (ID INT PRIMARY KEY NOT NULL,
  NAME           TEXT NOT NULL,
  AGE            INT NOT NULL);"""
)

print("Table created successfully")


conn.execute(
    "INSERT INTO USER (ID, NAME, AGE) \
  VALUES(1, 'Ajitha', 69)"
)
conn.execute(
    "INSERT INTO USER (ID, NAME, AGE) \
  VALUES(2, 'Ajitha2', 42)"
)
conn.execute(
    "INSERT INTO USER (ID, NAME, AGE) \
  VALUES(3, 'Ajitha3', 156)"
)

conn.commit()
print("Records created successfully")

items = conn.execute("SELECT id, name, age from USER")

for row in items:
    print("Id= ", row[0])
    print("name= ", row[1])
    print("age= ", row[2])

print("Operations done successfully")

conn.close()
