from fastapi import FastAPI
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

mongo_uri = os.getenv(
    "MONGO_URL")
client = MongoClient(mongo_uri)

db = client.get_database("redilab")
files = client.get_database("filedb")
collection = db.get_collection("users")
infos = db.get_collection("infos")
