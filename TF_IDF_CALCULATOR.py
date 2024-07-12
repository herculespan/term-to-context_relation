import os
import re
from DB import DB
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np  # Ensure NumPy is imported
from dotenv import load_dotenv

class TF_IDF_CALCULATOR:
    corpus = []
    tfidf_scores = []
    vocabulary = []
    db = None
    collection_name = ''
    word_scores = {}

    def __init__(self):
        load_dotenv()
        self.db = DB()
        self.collection_name = os.getenv("MONGO_ABSTRACTS_COLLECTION", "abstracts")

        self.db.empty_collection('term_scores')

        abstracts = self.db.fetch(self.collection_name, {})
        self.corpus = [abstract["preprocessed_text"] for abstract in abstracts]
        self.compute()
        print(self.vocabulary)
        print(self.tfidf_scores)

        distinct_terms = self.db.distinct('crawler', 'term')
        word_scores = {}

        # Calculate average TF-IDF scores only for distinct terms
        for term in distinct_terms:
            try:
                term = term.lower()
                pos = np.where(self.vocabulary == term)[0][0]  # Find index of the term in the vocabulary array
                values = self.tfidf_scores[:, pos]
                word_scores[term] = sum(values) / len(values)
            except IndexError:
                word_scores[term] = 0  # Default score for terms not in the vocabulary

        print(word_scores)

        # Create records to insert into the database
        scores = [{"term": term.lower(), "score": word_scores[term.lower()]} for term in distinct_terms]

        self.db.insert_records(scores, 'term_scores')

        self.db.close_connection()

    def compute(self):
      ''' The function receives a corpus of texts provided in the form of a list
      and a term and returns the term's tf-idf score for all the corpus texts it
      appears in.'''

      # Creation of a vectorizer object and fitting it to the pre-processed corpus.
      vectorizer = TfidfVectorizer()
      vectorizer.fit(self.corpus)

      # The pre-processed corpus is transformed to a a mtrix of tf-idf scores.
      self.tfidf_scores =  vectorizer.transform(self.corpus).toarray()
      self.vocabulary = vectorizer.get_feature_names_out()