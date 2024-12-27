from flask import Flask, render_template, request, send_from_directory, url_for
import json
import os
import snowballstemmer

app = Flask(__name__)

stemmer = snowballstemmer.stemmer('english')

# Positional index
with open('../token_dict_positional.json', 'r') as json_file:
    token_dict = json.load(json_file)

# Load the TF-IDF data
with open('tfidf.json', 'r') as tfidf_file:
    tfidf_data = json.load(tfidf_file)

# Directory where documents are stored
documents_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'documents_separated'))


def get_document_subject(document_id):
    file_path = os.path.join(documents_directory, f"{document_id}.txt")
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            for line in file:
                if line.startswith('Subject:'):
                    return line[len('Subject:'):].strip()
    except FileNotFoundError:
        return "Document not found"
    return "Subject not found"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])  # Allow both GET and POST methods
def search():
    if request.method == 'POST':
        query = request.form.get('query', '').lower()
        page = 1  # Reset to the first page on a new search
    else:
        query = request.args.get('query', '').lower()  # Use GET for pagination
        page = int(request.args.get('page', 1))  # Get current page number

    results_per_page = 20  # Number of results to display per page
    results = []

    if query:
        tokens = query.split()
        stemmed_tokens = [stemmer.stemWord(token) for token in tokens]
        matched_documents = None

        for token in stemmed_tokens:
            if token in token_dict:
                current_documents = set(token_dict[token].keys())
                if matched_documents is None:
                    matched_documents = current_documents
                else:
                    matched_documents &= current_documents

        if matched_documents:
            for document_id in matched_documents:
                subject = get_document_subject(document_id)
                document_link = url_for('send_document', filename=f'{document_id}.txt')
                token_positions = {}
                total_frequency = 0
                tfidf_score = 0

                # Calculate frequency and TF-IDF score
                for token in stemmed_tokens:
                    if token in token_dict and document_id in token_dict[token]:
                        positions = token_dict[token][document_id]
                        token_positions[token] = positions
                        total_frequency += len(positions)

                        # Add TF-IDF score if it exists in tfidf_data
                        if document_id in tfidf_data and token in tfidf_data[document_id]:
                            tfidf_score += tfidf_data[document_id].get(token, 0)

                # Add the result with both frequency and TF-IDF score
                results.append({
                    "document_id": document_id,
                    "subject": subject,
                    "total_frequency": total_frequency,
                    "tfidf_score": tfidf_score,
                    "token_positions": token_positions,
                    "link": document_link
                })

    # Combine frequency and TF-IDF for a final relevance score
    for result in results:
        result["final_score"] = result["total_frequency"] + result["tfidf_score"]

    # Sort results by the final relevance score (higher = more relevant)
    sorted_results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    # Pagination logic
    total_results = len(sorted_results)
    start = (page - 1) * results_per_page
    end = start + results_per_page
    paginated_results = sorted_results[start:end]

    # Calculate total pages
    total_pages = (total_results + results_per_page - 1) // results_per_page

    return render_template('results.html', query=query, results=paginated_results, page=page, total_pages=total_pages)


@app.route('/documents/<path:filename>', methods=['GET'])
def send_document(filename):
    return send_from_directory(documents_directory, filename)


if __name__ == '__main__':
    app.run(debug=True)
