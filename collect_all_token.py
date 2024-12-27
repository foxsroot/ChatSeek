import os
import string
import nltk
from nltk.corpus import stopwords
import json

# Directory containing documents
directory = 'documents_separated'

# Download NLTK stopwords
nltk.download('stopwords')

# Remove punctuation from tokens
def remove_punctuation_from_tokens(tokens):
    translator = str.maketrans('', '', string.punctuation)
    tokens = [token.translate(translator) for token in tokens]
    return [token for token in tokens if token]

# Tokenize and clean text
def tokenize(sentence):
    sentence = sentence.replace("\n", " ").replace("\t", " ").lower()
    tokens = sentence.split(" ")
    tokens = remove_punctuation_from_tokens(tokens)
    filtered_words = [word for word in tokens if word not in stopwords.words('english')]
    return filtered_words

# Initialize a set to store unique tokens
unique_tokens = set()

# Process each document
progress = 0
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()
        
        tokens = tokenize(content)
        unique_tokens.update(tokens)
    
    progress += 1
    print(f"Processed {progress} / 15033")

# Save all unique tokens to a JSON file
with open('search_engine/all_tokens.json', 'w') as json_file:
    json.dump(list(unique_tokens), json_file, indent=4)

print("!!!!!!!!!!!!!!!DONE!!!!!!!!!!!!!!")
print("All unique tokens have been saved to all_tokens.json.")
