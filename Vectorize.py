import sys

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertModel, BertTokenizer
from AbstractDataset import AbstractDataset
from DB import DB

class Vectorize:
    PRE_TRAINED_WEIGHTS = "recobo/agriculture-bert-uncased"
    MAX_LENGTH = 512
    model = None
    tokenizer = None
    BATCH_SIZE = 1
    terms_tokens = {}

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = BertModel.from_pretrained(self.PRE_TRAINED_WEIGHTS, output_hidden_states=True).to(self.device)
        self.tokenizer = BertTokenizer.from_pretrained(self.PRE_TRAINED_WEIGHTS)
        self.db = DB()
        self.terms_tokens = {}
        for term in self.db.fetch("term_scores", {}):
            self.terms_tokens[term["term"]] = term["tokens"]

        self.db.empty_collection('raw_abstract_vectors')
        # print(torch.cuda.is_available())  # Check if CUDA is available
        # print("Device:", torch.cuda.get_device_name(0))
        # sys.exit(1)

        print(self.terms_tokens)

    def run(self, corpus):
        print(len(corpus), "documents to vectorize")

        texts = [abstract["text"] for abstract in corpus]

        dataset = AbstractDataset(texts, self.tokenizer, self.MAX_LENGTH)
        dataloader = DataLoader(dataset, batch_size=self.BATCH_SIZE, shuffle=False)

        with torch.no_grad():
            for batch_index, batch_data in enumerate(dataloader):
                print("Batch index",batch_index, batch_data["text"])
                input_ids = batch_data["input_ids"].squeeze(1).to(self.device)
                attention_mask = batch_data["attention_mask"].squeeze(1).to(self.device)
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

                tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0, :])
                print("tokens", tokens, len(tokens), type(tokens))
                abstract = None
                # print(outputs.last_hidden_state[:, 0, :])
                cls_vectors = outputs.last_hidden_state[:, 0, :]
                for index, vector in enumerate(cls_vectors):
                    abstract = corpus[(batch_index*self.BATCH_SIZE)+index]
                    # print(vector, vector.shape, abstract["id"], abstract["text"][:10] + "...")
                    print('update id', abstract["id"])
                    self.db.update_record("abstracts", abstract["id"], {"vector": vector.numpy().tolist()})

                abstract_vectors = self.get_abstract_vectors_per_term(abstract, tokens, outputs.last_hidden_state)
                print(abstract_vectors)
                if abstract_vectors is not None and len(abstract_vectors) > 0:
                    self.db.insert_records(abstract_vectors, "raw_abstract_vectors")

        self.db.close_connection()

    def get_abstract_vectors_per_term(self, abstract, tokens, outputs):
        token_positions_per_term = self.get_abstract_token_positions_per_term(abstract, tokens)
        print("token_positions_per_term", token_positions_per_term)
        result = []
        for term_tokens in token_positions_per_term:
            vectors = self.get_token_vectors(outputs, term_tokens["token_positions"])
            result.append({"abstract": abstract["id"], "term": term_tokens["term"], "vectors": vectors})

        return result
    def get_abstract_token_positions_per_term(self, abstract, tokens):
        abstract_related_terms = abstract["terms"].keys()
        print("abstract_related_terms", abstract_related_terms)
        terms_positions = []
        for abstract_related_term in abstract_related_terms:
            abstract_related_term = abstract_related_term.lower()
            term_tokens = self.terms_tokens[abstract_related_term]  # array of tokens
            print("term_tokens", term_tokens)

            token_positions = self.find_token_positions(tokens, term_tokens)
            terms_positions.append({"term": abstract_related_term, "token_positions": token_positions})
            print("token_positions", token_positions)

        return terms_positions
    def get_token_vectors(self, output_tensor, token_occurrences):
        vectors = []
        for occurrence in token_occurrences:
            occurrence_vector = []
            for token_position in occurrence:
                occurrence_vector.append(output_tensor[0, token_position, :].numpy().tolist())
            vectors.append(occurrence_vector)
        return vectors
    def find_token_positions(self, token_pool, find_tokens):
        window = len(find_tokens)
        indexes = []
        for index, token in enumerate(token_pool):
            if index + window < len(token_pool):
                if token == find_tokens[0]:
                    if token_pool[index:index + window] == find_tokens:
                        indexes.append([pos for pos in range(index, index + window)])

        return indexes
    def tokenize_terms(self):
        db = DB()

        for term in db.fetch("term_scores", {}):
            tokens = self.tokenizer.tokenize(term["term"])
            db.update_record("term_scores", term["_id"], {"tokens": tokens})
            print(tokens, type(tokens))

        db.close_connection()