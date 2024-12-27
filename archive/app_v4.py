from flask import Flask, render_template, request, send_from_directory, url_for
import json
import os
import snowballstemmer

app = Flask(__name__)

# Initialize the English stemmer
stemmer = snowballstemmer.stemmer('english')

# Load the filtered token dictionary with positional index
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


def tokens_are_adjacent(token_positions):
    if not token_positions or len(token_positions) < 2:
        return True  # Single token query is always valid
    sorted_positions = sorted(token_positions.items(), key=lambda x: x[1][0])
    positions = [pos[1] for pos in sorted_positions]

    for i in range(len(positions) - 1):
        found_adjacent = False
        for pos1 in positions[i]:
            for pos2 in positions[i + 1]:
                if 0 <= (pos2 - pos1) <= 2:  # Allow one stopword in between
                    found_adjacent = True
                    break
            if found_adjacent:
                break
        if not found_adjacent:
            return False
    return True

def get_email(document_id):
    file_path = os.path.join(documents_directory, f"{document_id}.txt")
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            for line in file:
                if line.startswith("From:"):
                    return line.split("From:", 1)[1].strip().split(" ")[0]
    except FileNotFoundError:
        return "Document not found"

    return "Email not found"

def get_newsgroup(document_id):
    file_path = os.path.join(documents_directory, f"{document_id}.txt")
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            for line in file:
                if line.startswith("Newsgroup:"):
                    return line.split("Newsgroup:", 1)[1].strip()
    except FileNotFoundError:
        return "Document not found"

    return "Email not found"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query', '').lower()
        page = 1
    else:
        query = request.args.get('query', '').lower()
        page = int(request.args.get('page', 1))

    results_per_page = 20
    results = []

    if query:
        tokens = query.split()
        stemmed_tokens = [stemmer.stemWord(token) for token in tokens]
        matched_documents = set()

        if len(stemmed_tokens) == 1:
            token = stemmed_tokens[0]
            if token in token_dict:
                matched_documents = set(token_dict[token].keys())
        else:
            for token in stemmed_tokens:
                if token in token_dict:
                    current_documents = set(token_dict[token].keys())
                    if matched_documents:
                        matched_documents &= current_documents
                    else:
                        matched_documents = current_documents

        if matched_documents:
            for document_id in matched_documents:
                subject = get_document_subject(document_id)
                document_link = url_for('send_document', filename=f'{document_id}.txt')
                token_positions = {}
                tfidf_score = 0

                # For each token, accumulate TF-IDF score
                for token in stemmed_tokens:
                    if token in token_dict and document_id in token_dict[token]:
                        positions = token_dict[token][document_id]
                        token_positions[token] = positions
                        if document_id in tfidf_data and token in tfidf_data[document_id]:
                            tfidf_score += tfidf_data[document_id].get(token, 0)

                # If the query has only one token or the tokens are adjacent
                if len(stemmed_tokens) == 1 or tokens_are_adjacent(token_positions):
                    results.append({
                        "document_id": document_id,
                        "subject": subject,
                        "tfidf_score": tfidf_score,
                        "token_positions": token_positions,
                        "link": document_link,
                        "email": get_email(document_id),
                        "newsgroup": get_newsgroup(document_id)
                    })

    # Sort by the TF-IDF score (descending order)
    sorted_results = sorted(results, key=lambda x: x["tfidf_score"], reverse=True)

    total_results = len(sorted_results)
    start = (page - 1) * results_per_page
    end = start + results_per_page
    paginated_results = sorted_results[start:end]

    total_pages = (total_results + results_per_page - 1) // results_per_page

    return render_template('results.html', query=query, results=paginated_results, page=page, total_pages=total_pages)


@app.route('/documents/<path:filename>', methods=['GET'])
def send_document(filename):
    return send_from_directory(documents_directory, filename)


if __name__ == '__main__':
    app.run(debug=True)