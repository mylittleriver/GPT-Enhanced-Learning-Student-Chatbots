import sqlite3

db_path = "chatbot.db"  
conn = sqlite3.connect(db_path)

cursor = conn.cursor()
# conn.execute("PRAGMA journal_mode=WAL;")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"Columns in table '{table_name}':")
    for column in columns:
        print(column[1])
# cursor.execute("SELECT * FROM system_prompt;")
# records = cursor.fetchall()
# print("records:", records)

# cursor.execute("SELECT * FROM quiz_topic WHERE course_id='CS123';")
# records = cursor.fetchall()
# print("quiz records:", records)

# cursor.execute("INSERT INTO correctness_api VALUES ('CS5489', 0)")
# cursor.execute("INSERT INTO correctness_api VALUES ('CS3342', 0)")
# cursor.execute("INSERT INTO correctness_api VALUES ('CS6493', 0)")
# cursor.execute("INSERT INTO correctness_api VALUES ('CS2402', 0)")
# cursor.execute("INSERT INTO correctness_api VALUES ('CS4386', 0)")
# cursor.execute("INSERT INTO correctness_api VALUES ('CS2311', 0)")
# cursor.execute("INSERT INTO correctness_api VALUES ('CS4186', 0)")
# cursor.execute("DELETE FROM all_questions WHERE course_id = ?", ('CS5489',))

# # # 确保提交更改
# conn.commit()

# # 打印更新后的记录
# cursor.execute("SELECT * FROM correctness_api;")
# records = cursor.fetchall()
# for record in records:
#     print(record)

# cursor.execute("SELECT * FROM all_questions WHERE course_id = 'CS5489';")
# records = cursor.fetchall()
# for record in records:
#     print(record)

# cursor.execute("SELECT * FROM quiz_topic WHERE course_id='CS123';")
# records = cursor.fetchall()
# for record in records:
#     print(record)

cursor.close()
conn.close()  # 关闭数据库连接，释放锁
