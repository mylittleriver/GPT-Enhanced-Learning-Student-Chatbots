import sqlite3

db_path = "chatbot.db"  
conn = sqlite3.connect(db_path)

cursor = conn.cursor()
conn.execute("PRAGMA journal_mode=WAL;")

# cursor.execute('''
# CREATE TABLE IF NOT EXISTS quiz_mistakes (
#     course_id TEXT NOT NULL,
#     student_id TEXT NOT NULL,
#     quiz_name TEXT NOT NULL,
#     incorrect_question TEXT NOT NULL
# )
# ''')

# # 提交更改并关闭连接
# conn.commit()

# print("Table 'quiz_mistakes' created successfully.")

# cursor.execute("DROP TABLE IF EXISTS user_topics;")
# conn.commit()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS quizzer_incorrect_responses (
#     r_id TEXT PRIMARY KEY,
#     user_content TEXT NOT NULL,
#     response_content TEXT NOT NULL,
#     course_id TEXT NOT NULL,
#     topic TEXT NOT NULL
# );
# """)

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS user_quizzes (
#         course_id TEXT,
#         student_id TEXT,
#         quiz_name TEXT,
#         quiz_sc TEXT
#     );
# ''')

# conn.commit()
# conn.close()

# # 1. 重命名原表
# cursor.execute('''
#     ALTER TABLE user_quizzes RENAME TO user_quizzes_old;
# ''')

# # 2. 创建新表，列名已更新
# cursor.execute('''
#     CREATE TABLE user_quizzes (
#         course_id TEXT,
#         student_id TEXT,
#         quiz_name TEXT,
#         accuracy TEXT
#     );
# ''')

# # 3. 从旧表复制数据到新表
# cursor.execute('''
#     INSERT INTO user_quizzes (course_id, student_id, quiz_name, accuracy)
#     SELECT course_id, student_id, quiz_name, quiz_sc FROM user_quizzes_old;
# ''')

# # 4. 删除旧表
# cursor.execute('''
#     DROP TABLE user_quizzes_old;
# ''')

# # 5. 提交更改并关闭连接
# conn.commit()

# # 1. 重命名原表
# cursor.execute('''
#     ALTER TABLE user_quizzes RENAME TO user_quizzes_old;
# ''')

# # 2. 创建新表，accuracy 列为 FLOAT 类型
# cursor.execute('''
#     CREATE TABLE user_quizzes (
#         course_id TEXT,
#         student_id TEXT,
#         quiz_name TEXT,
#         accuracy FLOAT
#     );
# ''')

# # 3. 拷贝数据并尝试将 accuracy 转换为 FLOAT
# cursor.execute('''
#     INSERT INTO user_quizzes (course_id, student_id, quiz_name, accuracy)
#     SELECT course_id, student_id, quiz_name, CAST(accuracy AS FLOAT) FROM user_quizzes_old;
# ''')

# # 4. 删除旧表
# cursor.execute('''
#     DROP TABLE user_quizzes_old;
# ''')

# # 5. 提交更改并关闭连接
# conn.commit()

cursor.execute('SELECT * FROM quiz_mistakes;')
rows = cursor.fetchall()
for row in rows:
    print(row)

# cursor.execute('SELECT * FROM user_passed_quizzes;')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# # 重命名 user_quizzes 表为 user_passed_quizzes
# for table in tables:
#     table_name = table[0]
#     if table_name == "user_quizzes":
#         cursor.execute("ALTER TABLE user_quizzes RENAME TO user_passed_quizzes;")
#         print("Renamed table 'user_quizzes' to 'user_passed_quizzes'.")

# # 重新查询所有表，确认改名成功
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()
# print("Tables in the database after renaming:", tables)

# # 打印每张表的列信息
# for table in tables:
#     table_name = table[0]
#     cursor.execute(f"PRAGMA table_info({table_name});")
#     columns = cursor.fetchall()
#     print(f"Columns in table '{table_name}':")
#     for column in columns:
#         print(f"{column[1]} ({column[2]})")

# cursor.execute("SELECT COUNT(*) FROM quiz_topic;")
# count = cursor.fetchone()[0]
# print(f"Number of records in 'quiz_topic': {count}")

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
