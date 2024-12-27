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

    # If the term appears in every document, set IDF to 0
    if document_frequency == total_documents:
        idf = 0
    else:
        # Inverse Document Frequency (with smoothing)
        idf = math.log((total_documents + 1) / (document_frequency + 1)) + 1

    for doc_id, positions in postings.items():
        # Term Frequency (Log normalization)
        tf = 1 + math.log(len(positions)) if len(positions) > 0 else 0

        # TF-IDF calculation
        tf_idf_value = tf * idf

        # Store TF-IDF value
        if doc_id not in tfidf:
            tfidf[doc_id] = {}
        tfidf[doc_id][term] = tf_idf_value

# Optional: Normalize TF-IDF per document
for doc_id, terms in tfidf.items():
    norm = math.sqrt(sum(value ** 2 for value in terms.values()))
    if norm > 0:
        for term in terms:
            terms[term] /= norm

# Save TF-IDF values to a JSON file
with open('search_engine/tfidf_v3.json', 'w') as json_file:
    json.dump(tfidf, json_file, indent=4)

print("TF-IDF calculation complete with normalization.")