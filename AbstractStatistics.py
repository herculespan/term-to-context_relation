from DB import DB


class AbstractStatistics:
    def __init__(self):
        pass

    def run(self):
        db = DB()
        terms = db.distinct("crawler", "term")
        for abstract in db.fetch("abstracts", {}):
            occurrences = self.find_word_positions(abstract['clean_text'], terms)
            word_count = len(abstract['clean_text'].split())
            terms_count = len(occurrences)

            db.update_record("abstracts", abstract["_id"], {"term_occurrences": occurrences, "word_count": word_count, "terms_count": terms_count})
            print(occurrences, word_count)
        pass

        db.close_connection()

    def find_word_positions(self, text, words):
        positions = {}
        # Convert the text to lowercase to ensure case-insensitive matching
        lower_text = text.lower()
        for word in words:
            # Also convert the word to lowercase
            lower_word = word.lower()
            start = 0
            # Find all occurrences of the word
            while True:
                start = lower_text.find(lower_word, start)
                if start == -1:  # No more occurrences
                    break
                if word in positions:
                    positions[word].append(start)
                else:
                    positions[word] = [start]
                start += len(lower_word)  # Move past the current found word
        return positions
