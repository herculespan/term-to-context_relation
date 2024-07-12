import numpy as np
from scipy.spatial.distance import cosine
from DB import DB


class OccurrenceAbstractSemanticDistances:

    def __init__(self, term):
        self.db = DB()
        self.term = term
        self.abstracts = []
        self.terms = self.db.fetch('term_scores', {})
        self.term_ids = {}

        for term in self.terms:
            self.term_ids[term['term']] = term['_id']

    def get_abstracts(self):
        crawler_ids = [item["_id"] for item in self.db.fetch('crawler', {"term": self.term})]
        print(crawler_ids)
        return self.db.fetch('abstracts', {"crawler_id": {"$in": crawler_ids}})

    def get_mean_vectors_by_abstract_id(self, abstract_id):
        return self.db.fetch('mean_pooled_abstract_vectors', {"abstract": abstract_id})

    @staticmethod
    def run(term):
        print('Running OccurrenceAbstractSemanticDistances for ', term)
        obj = OccurrenceAbstractSemanticDistances(term)
        obj.abstracts = obj.get_abstracts()

        distances = []
        for abstract in obj.abstracts:
            occurrence_vectors = obj.get_mean_vectors_by_abstract_id(abstract["_id"])
            if len(list(occurrence_vectors.clone())) != 1:
                continue

            abstract_vector = np.array(abstract['vector'])
            for occurrence_vector in occurrence_vectors[0]['vectors']:
                occurrence_vector = np.array(occurrence_vector)
                distances.append(cosine(abstract_vector, occurrence_vector))

        obj.db.update_record('term_scores', obj.term_ids.get(term), {
            'occurrence_abstract_distances': distances,
            'average_occurrence_abstract_distance': sum(distances) / len(distances)
        })

        print(distances, len(distances))
