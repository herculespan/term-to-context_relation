import os
from dotenv import load_dotenv
import pymongo
class DB:
    def __init__(self):
        load_dotenv()
        print(os.getenv("MONGO_DSN"))
        self.client = pymongo.MongoClient(os.getenv("MONGO_DSN"))
        self.db = self.client[os.getenv("MONGO_DB")]
        print("DB Connection opened")

    def close_connection(self):
        self.client.close()
        print("DB Connection closed")

    def insert_record(self, record, collection_name: str):
        self.db[collection_name].insert_one(record)

    def insert_records(self, records, collection_name: str):
        self.db[collection_name].insert_many(records)

    def delete_many(self, query, collection_name: str):
        self.db[collection_name].delete_many(query)

    def empty_collection(self, collection_name: str):
        self.db[collection_name].delete_many({})

    def fetch_by_status(self, collection_name: str, status:str, limit: int = 1):
        return self.db[collection_name].find({"status": status}).limit(limit)

    def fetch(self, collection_name: str, query: dict, limit: int|None = None):
        if limit is None:
            return self.db[collection_name].find(query)
        else:
            return self.db[collection_name].find(query).limit(limit)

    def update_record(self, collection_name: str, record_id, data):
        self.db[collection_name].update_one({"_id": record_id}, {"$set": data})

    def distinct(self, collection_name: str, field: str):
        return self.db[collection_name].distinct(field)