import sqlite3

db_path = "chatbot.db"  
conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)
cursor.execute("SELECT * FROM quiz_topic WHERE course_id='CS123';")
records = cursor.fetchall()
print("quiz records:", records)
