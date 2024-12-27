from flask import Flask, render_template, request, send_from_directory, url_for
import json
import os
import snowballstemmer

app = Flask(__name__)
stemmer = snowballstemmer.stemmer('english')

with open('token_dict_positional.json', 'r') as json_file:
    token_dict = json.load(json_file)

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
        return False
    sorted_positions = sorted(token_positions.items(), key=lambda x: x[1][0])
    positions = [pos[1] for pos in sorted_positions]

    for i in range(len(positions) - 1):
        found_adjacent = False
        for pos1 in positions[i]:
            for pos2 in positions[i + 1]:
                if 0 <= (pos2 - pos1) <= 2:
                    found_adjacent = True
                    break
            if found_adjacent:
                break
        if not found_adjacent:
            return False
    return True


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

                for token in stemmed_tokens:
                    if token in token_dict and document_id in token_dict[token]:
                        positions = token_dict[token][document_id]
                        token_positions[token] = positions
                        total_frequency += len(positions)

                if len(tokens) > 1:
                    if tokens_are_adjacent(token_positions):
                        results.append({
                            "document_id": document_id,
                            "subject": subject,
                            "total_frequency": total_frequency,
                            "token_positions": token_positions,
                            "link": document_link
                        })
                else:
                    results.append({
                        "document_id": document_id,
                        "subject": subject,
                        "total_frequency": total_frequency,
                        "token_positions": token_positions,
                        "link": document_link
                    })

    total_results = len(results)
    start = (page - 1) * results_per_page
    end = start + results_per_page
    paginated_results = results[start:end]

    total_pages = (total_results + results_per_page - 1) // results_per_page

    return render_template('results.html', query=query, results=paginated_results, page=page, total_pages=total_pages)


@app.route('/documents/<path:filename>', methods=['GET'])
def send_document(filename):
    return send_from_directory(documents_directory, filename)


if __name__ == '__main__':
    app.run(debug=True)