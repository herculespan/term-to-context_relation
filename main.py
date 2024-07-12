import sys

from AGRIS import Agris
from CrawlerStatus import CrawlerStatus
from Preprocessor import Preprocessor
from AbstractStatistics import AbstractStatistics
from Vectorize import Vectorize
from Corpus import Corpus
from MeanPooling import MeanPooling

from DB import DB
from OccurrenceSemanticDistances import OccurrenceSemanticDistances
from OccurrenceAbstractSemanticDistances import OccurrenceAbstractSemanticDistances
from AbstractSemanticDistances import AbstractSemanticDistances


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from TF_IDF_CALCULATOR import TF_IDF_CALCULATOR


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) < 1:
        print("Usage: python main.py <search_term> [search_params]")
        sys.exit(1)

    command = sys.argv[1]
    params = sys.argv[2:]

    match command:
        case "prepare":
            print('Preparing to fetch data for:', params)
            agris = Agris()
            for term in params:
                print('Fetching data for:', term)
                agris.fetchTermAbstracts(term)
        case "crawl":
            agris = Agris()
            agris.fetchAbstracts(int(params[0]) if params else None)
        case 'clear':
            db = DB()
            for collection_name in params:
                db.empty_collection(collection_name)
            db.close_connection()
        case 'preprocess':
            Preprocessor().run()
        case 'tfidf_calc':
            print('Calculating TF-IDF')
            TF_IDF_CALCULATOR()
        case 'fix_abstract':
            db = DB()
            for abstract in db.fetch('abstracts', {}):
                db.update_record(
                    'abstracts',
                    abstract['_id'],
                    {'clean_text': abstract['abstract']['clean'].replace("Show more [+]Less [-]", ' ')}
                )
            db.close_connection()
        case 'run_stats':
            AbstractStatistics().run()
        case 'vectorize':
            print('Vectorizing')

            # res = Vectorize().find_token_positions(['a', 'b', 'def', 'a', 'b', 'd', 'a', 'b', 'b', 'b'], ['d','a','b'])
            # print(res)
            Vectorize().run(Corpus.get(int(params[0]) if params else None))
        case 'mean_pooling':
            MeanPooling().run(int(params[0]) if params else None)
        case "tokenize_terms":
            Vectorize().tokenize_terms()
        case 'trim':
            db = DB()
            for abstract in db.fetch('abstracts', {}):
                db.update_record(
                    'abstracts',
                    abstract['_id'],
                    {'clean_text': abstract['clean_text'].strip()}
                )
            db.close_connection()
        case 'occurrence_distances':
            OccurrenceSemanticDistances.run("techniques")
        case 'occurrence_abstract_distances':
            OccurrenceAbstractSemanticDistances.run("techniques")
        case 'abstract_distances':
            AbstractSemanticDistances.run("techniques")
        case _:
            print("Invalid command")
