from flask import Flask, render_template, request, send_from_directory, url_for
import json
import os
import snowballstemmer
import re

app = Flask(__name__)
stemmer = snowballstemmer.stemmer('english')

with open('token_dict_positional.json', 'r') as json_file:
    token_dict = json.load(json_file)

with open('tfidf.json', 'r') as tfidf_file:
    tfidf_data = json.load(tfidf_file)

# Load all tokens for auto-suggestions
with open('all_tokens.json', 'r') as token_file:
    all_tokens = json.load(token_file)

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


def levenshtein_distance(s1, s2, max_distance=float('inf')):
    # Ensure that s1 is the shorter string to minimize space usage
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    previous_row = list(range(len(s1) + 1))

    for index2, char2 in enumerate(s2):
        current_row = [index2 + 1]

        for index1, char1 in enumerate(s1):
            if char1 == char2:
                current_row.append(previous_row[index1])
            else:
                current_row.append(
                    1 + min(previous_row[index1], previous_row[index1 + 1], current_row[-1])
                )

        if min(current_row) > max_distance:
            return max_distance + 1

        previous_row = current_row

    return previous_row[-1]


def auto_correct_query(tokens):
    corrected_tokens = []
    for token in tokens:
        closest_match = token
        min_distance = float('inf')
        max_distance = max(1, len(token) // 3)  # Max distance is 1/3 of token length

        for candidate in all_tokens:
            # Pass max_distance to levenshtein_distance for early termination
            distance = levenshtein_distance(token, candidate, max_distance)
            if distance <= max_distance and distance < min_distance:
                min_distance = distance
                closest_match = candidate

        corrected_tokens.append(closest_match)
    return corrected_tokens


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').lower()
    suggestions = []

    if query:
        suggestions = [token for token in all_tokens if token.startswith(query)][:10]

    return json.dumps(suggestions)


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

    corrected_query = query

    if query:

        tokens = query.split()
        tokens = [re.sub(r'[^a-zA-Z0-9]', '', token) for token in tokens]

        corrected_tokens = auto_correct_query(tokens)
        corrected_query = ' '.join(corrected_tokens)
        # corrected_query = query

        # if corrected_query != query:
        #     stemmed_tokens = [stemmer.stemWord(token) for token in corrected_tokens]
        # else:
        #     stemmed_tokens = [stemmer.stemWord(token) for token in tokens]

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

                for token in stemmed_tokens:
                    if token in token_dict and document_id in token_dict[token]:
                        positions = token_dict[token][document_id]
                        token_positions[token] = positions
                        if document_id in tfidf_data and token in tfidf_data[document_id]:
                            tfidf_score += tfidf_data[document_id].get(token, 0)

                if len(stemmed_tokens) == 1 or tokens_are_adjacent(token_positions):
                    results.append({
                        "subject": subject,
                        "tfidf_score": tfidf_score,
                        "link": document_link,
                        "email": get_email(document_id),
                        "newsgroup": get_newsgroup(document_id)
                    })

    sorted_results = sorted(results, key=lambda x: x["tfidf_score"], reverse=True)

    total_results = len(sorted_results)
    start = (page - 1) * results_per_page
    end = start + results_per_page
    paginated_results = sorted_results[start:end]

    total_pages = (total_results + results_per_page - 1) // results_per_page

    return render_template(
        'results.html',
        query=query,
        corrected_query=corrected_query,
        results=paginated_results,
        page=page,
        total_results=total_results,
        total_pages=total_pages
    )


@app.route('/documents/<path:filename>', methods=['GET'])
def send_document(filename):
    file_path = os.path.join(documents_directory, filename)
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            lines = file.readlines()

        content_start_index = 0
        for index, line in enumerate(lines):
            if line.strip() == "":
                content_start_index = index + 1
                break

        pruned_content = lines[content_start_index:]
        document_id = os.path.splitext(filename)[0]
        subject = get_document_subject(document_id)
        email = get_email(document_id)
        newsgroup = get_newsgroup(document_id)

        return render_template(
            'document.html',
            subject=subject,
            email=email,
            newsgroup=newsgroup,
            docID=document_id,
            content=''.join(pruned_content).replace('\n', '<br>')
        )
    except FileNotFoundError:
        return "Document not found", 404


if __name__ == '__main__':
    app.run(debug=True)