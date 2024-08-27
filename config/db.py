from fastapi import FastAPI
from pymongo import MongoClient
import os

app = FastAPI()

mongo_uri = os.getenv(
    "MONGO_URL", "mongodb+srv://ReDiUser:1234rtyu@cluster0.tnsqcvc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
print("MongoDB Verbindungs-URL:", mongo_uri)
client = MongoClient(mongo_uri)

db = client.get_database("redilab")
collection = db.get_collection("users")
infos = db.get_collection("infos")
