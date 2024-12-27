import os
import snowballstemmer
import string
import nltk
from nltk.corpus import stopwords
import json
from nltk.corpus.reader import documents

directory = 'documents_separated'
nltk.download('stopwords')
stemmer = snowballstemmer.stemmer('english')

def add_unique_key_value(data, key, value):
    if key not in data:
        data[key] = {value}
    else:
        data[key].add(value)

def remove_punctuation_from_tokens(tokens):
    translator = str.maketrans('', '', string.punctuation)
    tokens = [token.translate(translator) for token in tokens]
    return [token for token in tokens if token]

def tokenize(sentence):
    sentence = sentence.replace("\n", " ")
    sentence = sentence.replace("\t", " ")
    sentence = sentence.lower()
    tokens = sentence.split(" ")
    tokens = remove_punctuation_from_tokens(tokens)
    tokens = stemmer.stemWords(tokens)
    filtered_words = [word for word in tokens if word not in stopwords.words('english')]

    return filtered_words

token_dict = {}

progress = 0
document_id = 0

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path):
        document_id = os.path.splitext(filename)[0]

        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()

        tokens = tokenize(content)

        for token in tokens:
            add_unique_key_value(token_dict, token, document_id)

    progress += 1
    print(progress, "/", 15033)
    print("Document ID", document_id, " DONE")

print(token_dict)

with open('token_dict3.json', 'w') as json_file:
    json.dump({k: list(v) for k, v in token_dict.items()}, json_file)  # Convert sets to lists for JSON compatibility

print("!!!!!!!!!!!!!!!DONE!!!!!!!!!!!!!!")
print("token_dict has been saved to token_dict.json.")