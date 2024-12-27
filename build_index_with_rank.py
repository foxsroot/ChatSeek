import os
import snowballstemmer
import string
import nltk
from nltk.corpus import stopwords
import json

directory = 'documents_separated'
nltk.download('stopwords')
stemmer = snowballstemmer.stemmer('english')

def add_token_frequency(data, token, document_id):
    if token not in data:
        data[token] = {document_id: 1}
    else:
        if document_id in data[token]:
            data[token][document_id] += 1
        else:
            data[token][document_id] = 1

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
            add_token_frequency(token_dict, token, document_id)

    progress += 1
    print(progress, "/", 15033)
    print("Document ID", document_id, " DONE")

# Convert to list of tuples for sorting by frequency within each document
sorted_token_dict = {
    token: sorted(doc_dict.items(), key=lambda x: x[1], reverse=True)
    for token, doc_dict in token_dict.items()
}

with open('token_dict3.json', 'w') as json_file:
    json.dump(sorted_token_dict, json_file)  # Convert dict to JSON-compatible format

print("!!!!!!!!!!!!!!!DONE!!!!!!!!!!!!!!")
print("token_dict has been saved to token_dict.json.")
