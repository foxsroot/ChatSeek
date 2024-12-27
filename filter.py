import json

with open('token_dict3.json', 'r') as json_file:
    token_dict = json.load(json_file)

all_documents = set()
for token, doc_freq in token_dict.items():
    for document_id, _ in doc_freq:
        all_documents.add(document_id)

filtered_token_dict = {
    token: doc_freq
    for token, doc_freq in token_dict.items()
    if set(doc_id for doc_id, _ in doc_freq) != all_documents
}

with open('search_engine/filtered_token_dict.json', 'w') as json_file:
    json.dump(filtered_token_dict, json_file)

print("Filtered token dictionary has been saved to filtered_token_dict.json.")
