from flask import Flask, Response, render_template, request, url_for, send_from_directory
import json
import os
import snowballstemmer

app = Flask(__name__)
stemmer = snowballstemmer.stemmer('english')

with open('token_dict_positional.json', 'r') as json_file:
    token_dict = json.load(json_file)

# try:
#     with open('tfidf.json', 'r') as json_file:
#         tfidf = json.load(json_file)
# except FileNotFoundError:
#     tfidf = {}

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


# def expand_wildcard_query(wildcard_query, permuterm_index):
#     matched_terms = set()
#
#     if '*' in wildcard_query:
#         prefix, suffix = wildcard_query.split('*', 1)
#         query_with_end = prefix + '$' + suffix
#
#         for key in permuterm_index:
#             if key.startswith(query_with_end):
#                 original_term = key[-len(suffix) - 1:] + key[:-len(suffix) - 1]
#                 matched_terms.add(original_term.strip('$'))
#     else:
#         matched_terms.add(wildcard_query)
#
#     return list(matched_terms)


@app.route('/')
def home():
    """Render the homepage with a search form."""
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    def generate_results(query):
        """Stream results dynamically."""
        yield render_template('results.html', query=query, results=[])

        if query:
            print("Processing query:", query)  # Debug line

            # Check for wildcard and process query
            if '*' in query:
                expanded_terms = expand_wildcard_query(query, permuterm_index)
                stemmed_tokens = [stemmer.stemWord(term) for term in expanded_terms]
            else:
                tokens = query.split()
                stemmed_tokens = [stemmer.stemWord(token) for token in tokens]

            print("Stemmed tokens:", stemmed_tokens)  # Debug line

            matched_documents = None
            for token in stemmed_tokens:
                if token in token_dict:
                    current_documents = set(token_dict[token].keys())
                    matched_documents = (
                        current_documents if matched_documents is None
                        else matched_documents & current_documents
                    )

            print("Matched documents:", matched_documents)  # Debug line

            if matched_documents:
                for document_id in matched_documents:
                    subject = get_document_subject(document_id)
                    document_link = url_for('send_document', filename=f'{document_id}.txt')
                    token_positions = {}
                    total_frequency = 0
                    tfidf_score = 0.0

                    for token in stemmed_tokens:
                        if token in token_dict and document_id in token_dict[token]:
                            positions = token_dict[token][document_id]
                            token_positions[token] = positions
                            total_frequency += len(positions)

                            if document_id in tfidf and token in tfidf[document_id]:
                                tfidf_score += tfidf[document_id][token]

                    # Render and yield each document result
                    result_html = render_template('document.html',
                        subject=subject,
                        document_id=document_id,
                        tfidf_score=tfidf_score,
                        token_positions=token_positions,
                        link=document_link
                    )
                    yield result_html

        # Finalize HTML output
        yield "</div></body></html>"

    query = request.form.get('query', '').lower() if request.method == 'POST' else request.args.get('query', '').lower()
    return Response(generate_results(query), content_type='text/html')



@app.route('/documents/<path:filename>', methods=['GET'])
def send_document(filename):
    """Serve document files."""
    return send_from_directory(documents_directory, filename)


if __name__ == '__main__':
    app.run(debug=True)
