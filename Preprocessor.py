import re
import nltk

#nltk.download("punkt")
#nltk.download("stopwords")
# NLTK packages are installed to handle text pre-processing.
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from DB import DB


class Preprocessor:
    def __init__(self):
        pass

    def run(self):
        print("Preprocessor is running")
        # fetch all abstract

        db = DB()

        db.empty_collection("preprocessed_texts")
        abstracts = db.fetch("abstracts", {})

        for abstract in abstracts:
            print(abstract["abstract"]['clean'])
            preprocessed_text = self.text_preprocess(abstract["clean_text"])
            db.update_record("abstracts", abstract["_id"], {"preprocessed_text": preprocessed_text})
            print("================================")
            print(preprocessed_text)

        db.close_connection()

    def text_preprocess(self, text):
        ''' The function receives a text of arbitrary length as input and returns a
        pre-processed version of it. Pre-processing involves: (i) removal of any
        punctuation signs; (ii) segmentation of the text into words; and (iii) stopword
        removal.'''

        # Removal of punctuation signs and other non-alphanumerical characters.
        # The pattern used identifies any sequence that does not involve.
        text = re.sub("[^a-zA-Z]", " ", text)
        # The regular expression below will reduce the number of blank spaces in text from many to one.
        text = re.sub(r'\s+', ' ', text)

        # Text is lowercased and split into words using NLTK's word_tokenize function.
        words = word_tokenize(text.lower())

        # Stopword removal
        words = [word for word in words if word not in stopwords.words("english")]

        # The pre-processed version of the text is assembled by putting all the words together.
        preprocessed_text = " ".join(words)

        return preprocessed_text
