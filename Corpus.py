import sys

from DB import DB
from bson.objectid import ObjectId
class Corpus:
    @staticmethod
    def get(limit: int|None = 10):
        print('Fetching corpus....', limit)

        db = DB()
        abstracts = [{
            "id": abstract['_id'],
            "text": abstract['clean_text'],
            "terms": abstract["term_occurrences"],
            'crawler_id': abstract['crawler_id']
        } for abstract in db.fetch('abstracts', {}, limit)]
        #
        # print(abstracts)
        # sys.exit(1)


        # abstracts = [{
        #     "id": abstract['_id'],
        #     "text": abstract['clean_text'],
        #     "terms": abstract["term_occurrences"],
        # } for abstract in db.fetch('abstracts', {"crawler_id": ObjectId('664373e1c6c64e7aa3c90c26')}, limit)]

        db.close_connection()
        print('Fetched corpus....')
        return abstracts