from pymongo import MongoClient

# 🔴 Энд өөрийн connection string хийнэ
MONGO_URI = "mongodb+srv://greencampus:%40Pi07730@greencampus.k9oeyas.mongodb.net/"

client = MongoClient(MONGO_URI)

db = client["smart_campus"]
collection = db["sensor_data"]