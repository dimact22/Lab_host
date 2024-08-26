from fastapi import FastAPI
from pymongo import MongoClient
import os

app = FastAPI()

mongo_uri = os.getenv("MONGO_URL", "mongodb://localhost:27017/redilab")
print("MongoDB Verbindungs-URL:", mongo_uri)
client = MongoClient(mongo_uri)

db = client.get_database("redilab")
collection = db.get_collection("users")