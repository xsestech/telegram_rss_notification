import sqlite3


connection = sqlite3.connect("users.db", check_same_thread = True)
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"url"	TEXT
)""")


connection.commit()
connection.close()