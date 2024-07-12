import os

from DB import DB
from dotenv import load_dotenv
from CrawlerStatus import CrawlerStatus
import time

class Crawler:
    connection = None
    def __init__(self):
        load_dotenv()
        self.connection = DB()

    def queue(self, data: dict):
        self.connection.insert_records(data, os.getenv("MONGO_CRAWLER_COLLECTION","crawler"))

    def fetch_by_status(self, status:str, limit: int = 1):
        return self.connection.fetch_by_status(os.getenv("MONGO_CRAWLER_COLLECTION","crawler"), status,limit)

    def set_status(self, record_id, status):
        self.connection.update_record(os.getenv("MONGO_CRAWLER_COLLECTION","crawler"), record_id, {"status": status, "updated_at": time.time()})

    def save_abstract(self, data):
        self.connection.insert_record(data, os.getenv("MONGO_ABSTRACTS_COLLECTION", "abstracts"))

    def close(self):
        self.connection.close_connection()
