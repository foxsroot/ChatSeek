import json
import math

# Load token dictionary
with open('search_engine/token_dict_positional.json', 'r') as json_file:
    token_dict = json.load(json_file)

# Total number of documents
total_documents = len({
    doc_id
    for postings in token_dict.values()
    for doc_id in postings
})

# Calculate TF-IDF
tfidf = {}

for term, postings in token_dict.items():
    # Document frequency (number of documents containing the term)
    document_frequency = len(postings)

    # Inverse Document Frequency
    idf = math.log(total_documents / document_frequency)

    for doc_id, positions in postings.items():
        # Term Frequency (TF) is the count of positions
        tf = len(positions)

        # TF-IDF calculation
        tf_idf_value = tf * idf

        # Store TF-IDF value
        if doc_id not in tfidf:
            tfidf[doc_id] = {}
        tfidf[doc_id][term] = tf_idf_value

# Save TF-IDF values to a JSON file
with open('search_engine/archive/tfidf.json', 'w') as json_file:
    json.dump(tfidf, json_file, indent=4)

print("TF-IDF calculation complete.")
