# import json

# with open('token_dict.json', 'r') as file:
#     data = json.load(file)

# def search_key(json_obj, key):
#     if key in json_obj:
#         return json_obj[key]
#     else:
#         return f"Key '{key}' not found"


# key_to_search = "perceive"
# value = search_key(data, key_to_search)

# print(f"Value for '{key_to_search}': {value}")

import json

import nltk
import snowballstemmer
from nltk.tokenize import word_tokenize

# nltk.download('punkt_tab')

with open('token_dict2.json', 'r') as file:
    data = json.load(file)

stemmer = snowballstemmer.stemmer('english')

def stem_input_key(key):
    return stemmer.stemWords([key])[0]

def search_key(json_obj, key):
    tokens = word_tokenize(key)
    stemmed_tokens = [stem_input_key(token) for token in tokens]

    results = {}
    for stemmed_key in stemmed_tokens:
        if stemmed_key in json_obj:
            results[stemmed_key] = json_obj[stemmed_key]

    if len(stemmed_tokens) > 1:
        results = search_multi(results)

    return results if results else f"No keys found for the input: '{key}'"

def search_multi(results_set):
    all_documents = list(results_set.values())

    common_documents = set(all_documents[0]).intersection(*all_documents)

    if not common_documents:
        return "No common documents found across the keys"

    filtered_results = {}
    for key, documents in results_set.items():
        filtered_results[key] = [doc for doc in documents if doc in common_documents]

    return filtered_results

key_to_search = input("Input a string : ").lower()
value = search_key(data, key_to_search)

if isinstance(value, dict):
    keys = ', '.join(value.keys())
    first_key = next(iter(value))

    print(f"Documents containing {keys}: {', '.join(value.get(first_key))}\n")
else:
    print(value)


