import sys

from DB import DB
import numpy as np
from scipy.spatial.distance import cosine


class OccurrenceSemanticDistances:
    def __init__(self, term):
        self.db = DB()
        self.term_records = self.db.fetch('mean_pooled_abstract_vectors', {"term": term},30)
        self.vector_pool = []
        self.terms = self.db.fetch('term_scores', {})
        self.term_ids = {}

        for term in self.terms:
            self.term_ids[term['term']] = term['_id']

    @staticmethod
    def run(term):
        print('Running SemanticDistances for term:', term)
        obj = OccurrenceSemanticDistances(term)
        obj.construct_pool()

        term_distances = []
        for i in range(len(obj.vector_pool)):
            for j in range(i+1, len(obj.vector_pool)):
                term_distances.append(cosine(obj.vector_pool[i], obj.vector_pool[j]))

        obj.db.update_record('term_scores', obj.term_ids.get(term), {
            'occurrence_distances': term_distances,
            'average_occurrence_distance': sum(term_distances) / len(term_distances)
        })
        print(term_distances, len(term_distances), len(obj.vector_pool))

    def construct_pool(self):
        for vector_data in self.term_records:
            for vector in vector_data['vectors']:
                self.vector_pool.append(np.array(vector))