from pymongo import MongoClient

# client = MongoClient('mongodb://localhost:27017')
client = MongoClient('mongodb://127.0.0.1:27017')

db = client['gel_database']


