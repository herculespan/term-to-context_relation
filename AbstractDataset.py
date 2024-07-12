from torch.utils.data import Dataset
class AbstractDataset(Dataset):
    def __init__(self, sub_corpus, tokenizer, max_length):
        self.sub_corpus = sub_corpus
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.sub_corpus)

    def __getitem__(self, index):
        text = self.sub_corpus[index]
        encoding = self.tokenizer.encode_plus(text, add_special_tokens=True,
                                              padding="max_length", max_length=self.max_length,
                                              truncation=True, return_tensors="pt")
        # print('encoding', encoding)
        return {
            "text": text,
            "input_ids": encoding["input_ids"],
            "attention_mask": encoding["attention_mask"]
        }