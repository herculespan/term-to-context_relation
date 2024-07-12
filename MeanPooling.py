from DB import DB

class MeanPooling:

    def __init__(self):
        self.db = DB()
        self.RAW_ABSTRACT_COLLECTION = 'raw_abstract_vectors'
        self.MEAN_VECTORS_COLLECTION = 'mean_pooled_abstract_vectors'
        self.db.empty_collection(self.MEAN_VECTORS_COLLECTION)
        pass

    def run(self, limit: int = None):
        print('Start of MeanPooling')

        for raw_abstract in self.db.fetch(self.RAW_ABSTRACT_COLLECTION, {}, limit):
            print(raw_abstract["term"])
            mean_vectors = []
            for vector in raw_abstract["vectors"]:
                mean_vectors.append(self.calc_mean_pooling(vector))

            self.db.insert_record({
                "abstract": raw_abstract["abstract"],
                "term": raw_abstract["term"],
                "vectors": mean_vectors
            }, self.MEAN_VECTORS_COLLECTION)

    def calc_mean_pooling(self, vectors):
        if len(vectors) == 1:
            return vectors[0]
        else:
            print('Calculating mean pooling')
            print(len(vectors[0]))
            mean_vector = []
            for i in range(0, len(vectors[0])):
                mean_vector.append(sum([vector[i] for vector in vectors]) / len(vectors))

        return mean_vector