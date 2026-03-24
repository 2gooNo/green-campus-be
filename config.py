import os
from pymongo import MongoClient

# Mongo connection string from environment.
MONGO_URI = os.getenv("MONGO_URI")

# Shared Mongo client for the whole app.
client = MongoClient(MONGO_URI)

# Main database and collections.
db = client["smart_campus"]
collection = db["sensor_data"]
settings_collection = db["system_settings"]