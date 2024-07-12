import sys

from DB import DB
import numpy as np
from scipy.spatial.distance import cosine

class AbstractSemanticDistances:
    def __init__(self, term):
        self.db = DB()
        self.term = term
        self.terms = self.db.fetch('term_scores', {})
        self.term_ids = {}

        for term in self.terms:
            self.term_ids[term['term']] = term['_id']
        pass

    @staticmethod
    def run(term):
        print("AbstractSemanticDistances is running for ", term)
        obj = AbstractSemanticDistances(term)
        abstracts = obj.get_abstracts() #cursor

        cls_pool = []
        for abstract in abstracts:
            cls_pool.append(np.array(abstract['vector']))

        distances = []
        for i in range(len(cls_pool)):
            for j in range(i+1, len(cls_pool)):
                distances.append(cosine(cls_pool[i], cls_pool[j]))

        print(cls_pool, len(cls_pool))
        obj.db.update_record('term_scores', obj.term_ids.get(term), {
            'abstract_distances': distances,
            'average_abstract_distance': sum(distances) / len(distances)
        })

    def get_abstracts(self):
        crawler_ids = [item["_id"] for item in self.db.fetch('crawler', {"term": self.term})]
        return self.db.fetch('abstracts', {"crawler_id": {"$in": crawler_ids}})

