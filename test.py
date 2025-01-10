# import sqlite3

# # 连接到 SQLite 数据库
# conn = sqlite3.connect('chatbot.db')

# # 创建一个游标对象
# cursor = conn.cursor()


# # 执行 SQL 查询，选择 correctness_api 表中的所有记录
# cursor.execute("SELECT * FROM correctness_api")

# # 获取所有查询结果
# records = cursor.fetchall()

# # 打印所有记录
# for record in records:
#     print(record)

# # 执行 SQL 查询
# cursor.execute("SELECT * FROM system_prompt")

# # 获取所有行
# rows = cursor.fetchall()

# # 打印每一行
# for row in rows:
#     print(row)

# cursor.execute("SELECT * FROM all_questions LIMIT 1")

# # 获取列名
# column_names = [description[0] for description in cursor.description]
# print(column_names)

# 关闭连接

# conn.close()
from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017')
db = client['gel_database']
# chats_collection = db['chats']

# # 获取最近5条记录
# latest_chats = list(chats_collection.find().sort('_id', -1).limit(5))

# print(latest_chats)
# collections = db.list_collection_names()

# # 打印集合名称和描述信息
# for collection_name in collections:
#   print(f"Collection Name: {collection_name}")
  
#   # 获取集合
#   collection = db[collection_name]
  
#   # 检查集合是否为空
#   sample_document = collection.find_one()
#   if sample_document:
#       # 打印字段名称
#       print("Fields:", list(sample_document.keys()))
#   else:
#       print("This collection is empty.")
#   print("-" * 40)
topics_collection = db['topics']
chats_collection = db['chats']

# topic_id_value = "17190382279392558"  # 将此处替换为您的具体 topic_id
# query = {'chatbot_type': "tutor"}
# query = {'topic_id': topic_id_value}

# # 执行查询
# matching_chats = list(chats_collection.find(query))
# for chat in matching_chats:
#     print(chat)
# # 获取最近 8 条记录，根据 time 字段降序排序
# latest_chats = list(chats_collection.find().sort('time', -1).limit(20))
# latest_topics = list(topics_collection.find({"course_id": "CS5487"}).sort('_id', -1).limit(60))
# user_ids = list(
#     topics_collection.find({"course_id": "CS2313"}, {"user_id": 1, "_id": 0})
# )
user_id_count = topics_collection.aggregate([
    {"$group": {"_id": "$user_id"}},  # 按 user_id 分组
    {"$count": "unique_user_count"}  # 统计不同 user_id 的个数
])

result = list(user_id_count)
unique_user_count = result[0]['unique_user_count'] if result else 0

print("Number of unique user_id:", unique_user_count)
# latest_topic = topics_collection.find_one(sort=[('_id', -1)])
# query = {'topic_id': "17330675757721473"}
# matching_topics = list(topics_collection.find(query).limit(3))

# for topic in latest_topics:
#   print(topic)
# for uid in user_ids:
#   print(uid)

# for chat in latest_chats:
#   print(chat)
# for topic in matching_topics:
#   print(topic)
# 查询条件：chatbot_type 为 tutor_chatbot
# query = {'chatbot_type': 'quizzer_chatbot'}
# query = {'chatbot_type': None}

# 获取满足条件的前 20 条记录，根据 time 字段降序排序
# latest_chats = list(chats_collection.find(query).sort('time', -1).limit(20))

# 打印结果
# for chat in latest_chats:
#   print(chat)
# users_collection = db['users']

# # 查找 user_id 为 'shujunxia2' 的用户记录
# user = users_collection.find_one({"user_id": "shujunxia2"})

# if user:
#     # 打印当前用户记录
#     print("Current user record:", user)

