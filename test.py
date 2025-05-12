import json
import re

from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017')
db = client['gel_database']

document = db.courses.find_one({"course_id": "CS5487"})

if document:
    print("A record from 'courses' collection:", document)
else:
    print("The 'courses' collection is empty.")

# topics = db.topics.find({"course_id": 'CS5487', "chatbot_type": "quizzer"})
# user = db.users.find({"user_id": 'shujunxia2'})
# print(list(user))

# topics = list(db.topics.find({"course_id": 'CS4286'}, {"_id": 0, "latest_gpt_ver": 0}))
# topic_users = {topic["user_id"] for topic in topics}  

# print(topic_users)

# course_id='CS4186'
# selected_uid='nicoletse4'
# chatbot_type='quizzer'
# search_dict = {"course_id": course_id}
# if selected_uid != "" and selected_uid != "Select a user":
# 	search_dict["user_id"] = selected_uid
# if chatbot_type != "all":
# 	search_dict["chatbot_type"] = chatbot_type
# print('search_dict',search_dict)
# topics = db.topics.find(search_dict,{ "_id": 0, "latest_gpt_ver": 0})
# topics = list(topics)
# topic_users = {topic["user_id"] for topic in topics}  
# print('topic_users',topic_users)
# print('topics',topics)
# # topic_summaries = []  
# topic_data = {}
# for topic in topics:
#     topic_id = topic['topic_id']

#     chats = db.chats.find({"topic_id": topic_id})

#     for chat in chats:
#         chat_dict = quizzer_chat_parse(chat['content'])
#         topic_name = chat_dict.get("topic")
#         if topic_name is None:
#             continue
#         print('chat_dict',chat_dict)
#         question = chat_dict.get("question")
#         if topic_name not in topic_data:
#             topic_data[topic_name] = {"correct": [], "incorrect": []}
#         if question:
#             if chat_dict.get("correct") is True:
#                 topic_data[topic_name]["correct"].append(question)
#             elif chat_dict.get("incorrect") is True:
#                 topic_data[topic_name]["incorrect"].append(question)
# print(topic_data)

# topics_collection = db['topics']
# topics = db.topics.find(
#     {
#         "course_id": 'CS5487',
#         "chatbot_type": 'quizzer',
#     }
# ).sort('_id', -1).limit(55)
# topics = db.topics.find(
#     {
#         "course_id": 'CS5487',
#         "chatbot_type": 'tutor',
#     }
# )
# len_chat=0
# for topic in topics:
#     topic_id = topic['topic_id']

#     chats = db.chats.find({"topic_id": topic_id})
#     chats=list(chats)
#     for chat in chats:
#         print(chat)


# from collections import defaultdict
# import re

# helper=['manhlai', 'njaison2', 'shujunxia2', 'jiayuan']
# teacher_ids = db.courses.distinct("teacher_id")
# exclude_ids=helper+teacher_ids

# topics = db.topics.find(
# 			{
# 				"course_id": course_id,
# 				"chatbot_type": 'quizzer',
# 				"user_id": {"$nin": exclude_ids}
# 			}
# 		).sort("_id", -1)



# teacher_ids = db.courses.distinct("teacher_id")
# print(teacher_ids)
# user_id='bofang6'
# course_id='CS5489'
# topic_id='17385867368658163'
# topic_id='173997080842737'

# topic_list = db.topics.find({"topic_id": topic_id})
# print('topic_list by id',list(topic_list))

# topic_list = db.topics.find({"user_id": user_id})
# topic_list = list(topic_list)
# print('all course topic_list',topic_list)

# no_of_topics = len(topic_list)
# print('len all course topic_list', no_of_topics)

# no_of_chats = 0
# tokens_used = 0
# # Counting chats in each topic
# for topic in topic_list:
#     chat_list = db.chats.find({"topic_id": topic["topic_id"]}, {"_id": 0, "no_of_tokens": 1, "role": 1})
#     chat_list = list(chat_list)
#     no_of_chats += len(chat_list)
#     for chat in chat_list:
#         # previous bug: added user's tokens, which are 0s, should add assistant's tokens
#         # if chat["role"] == 'user':
#         if chat["role"] == 'assistant':
#             tokens_used += chat["no_of_tokens"]
# print('tokens_used',tokens_used)


# topic_list = db.topics.find({"user_id": user_id, "course_id": course_id}, {"_id": 0, "topic_id": 1, "course_id": 1})
# topic_list = list(topic_list)

# print('5489 topic_list',topic_list)

# no_of_topics = len(topic_list)
# print('len 5489 topic_list', no_of_topics)

# no_of_chats = 0
# tokens_used_in_course = 0
# # Counting chats in each topic
# for topic in topic_list:
#     chat_list = db.chats.find({"topic_id": topic["topic_id"]}, {"_id": 0, "no_of_tokens": 1, "role": 1})
#     chat_list = list(chat_list)
#     no_of_chats += len(chat_list)
#     for chat in chat_list:
#         # previous bug: added user's tokens, which are 0s, should add assistant's tokens
#         # if chat["role"] == 'user':
#         if chat["role"] == 'assistant':
#             tokens_used_in_course += chat["no_of_tokens"]
# print('tokens_used_in_course',tokens_used_in_course)

# topics = db.topics.find({"course_id": "CS5487", "chatbot_type": "quizzer"}).sort("_id", -1).limit(135)

# results = defaultdict(lambda: {"correct_cnt": 0, "incorrect_cnt": 0, "correct_questions": [], "incorrect_questions": []})

# for topic in topics:
#     topic_id = topic['topic_id']
    
#     chats = list(db.chats.find({"topic_id": topic_id}).sort("time", 1))
    
#     topic_name = None
#     question = None
#     user_answered = False
#     tracking_question = False
    
#     for chat in chats:
#         if chat['role'] == 'user' and "Generate a quiz question randomly from" in chat['content']:
#             continue  # Ignore quiz generation requests
        
#         if chat['role'] == 'assistant':
#             extracted_topic = extract_tag_content(chat['content'], 'topic')
#             extracted_question = extract_tag_content(chat['content'], 'question')
#             if extracted_topic and extracted_question:
#                 topic_name = extracted_topic  # Extract topic name from content
#                 question = extracted_question  # Start tracking a new question
#                 tracking_question = True
#                 user_answered = False
#                 continue
        
#         if tracking_question and chat['role'] == 'user':
#             user_answered = True  # User has responded to a question
#             continue
        
#         if user_answered and chat['role'] == 'assistant' and topic_name:
#             if '<correct>' in chat['content']:
#                 results[topic_name]["correct_questions"].append(question)
#                 results[topic_name]["correct_cnt"] += 1
#             elif '<incorrect>' in chat['content']:
#                 results[topic_name]["incorrect_questions"].append(question)
#                 results[topic_name]["incorrect_cnt"] += 1
#             question = None  # Reset for next question
#             user_answered = False
#             tracking_question = False

# Convert results to the desired format
# output = [
#     {
#         "topic": topic,
#         "correct_cnt": data["correct_cnt"],
#         "incorrect_cnt": data["incorrect_cnt"],
#         "correct_questions": data["correct_questions"],
#         "incorrect_questions": data["incorrect_questions"],
#     }
#     for topic, data in results.items()
# ]

# Print or save output
# import json
# print(json.dumps(output, indent=4, ensure_ascii=False))
#     len_chat+=len(chats)
# print(len_chat)
# for chat in chats:
#     print(chat['content'])
# latest_topics = list(topics_collection.find(
#     {'course_id': "CS5487", 'chatbot_type': "quizzer"}  
# ).sort('_id', -1))
# latest_topics = list(topics_collection.find(
#     {'topic_id': "17373417077733089"}  
# ).sort('_id', -1))
# topic_ids = [topic['topic_id'] for topic in latest_topics]
# print(topic_ids)
# print(len(topic_ids))
# chats_collection = db['chats']

# latest_chats = list(chats_collection.find({'topic_id': {'$in': topic_ids}}).sort('_id', -1))
# latest_chats = list(chats_collection.find().sort('_id', -1).limit(2))

# for chat in latest_chats:
#     print(chat,end='\n\n')
# print(latest_chats)

# courses_collection = db['courses']

# # 获取最近5条记录
# latest_courses = list(courses_collection.find().sort('_id', -1).limit(5))

# print(latest_courses)
# cs4186_course = courses_collection.find_one({'course_id': 'CS4186'})

# print(cs4186_course)

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
# topics_collection = db['topics']
# chats_collection = db['chats']
# q_collection = db['questions']
# query = {'course_id': "CS2313"}
# records = db.questions.find({'course_id': 'CS4182'})


# qs = list(q_collection.find(query))

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
# user_id_count = topics_collection.aggregate([
#     {"$group": {"_id": "$user_id"}},  # 按 user_id 分组
#     {"$count": "unique_user_count"}  # 统计不同 user_id 的个数
# ])

# result = list(user_id_count)
# unique_user_count = result[0]['unique_user_count'] if result else 0

# print("Number of unique user_id:", unique_user_count)
# latest_topic = topics_collection.find_one(sort=[('_id', -1)])
# query = {'topic_id': "17330675757721473"}
# matching_topics = list(topics_collection.find(query).limit(3))

# for topic in latest_topics:
#   print(topic)
# for uid in user_ids:
#   print(uid)

# for q in qs:
#   print(q)

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

