import os
import snowballstemmer
import string
import nltk
from nltk.corpus import stopwords
import json
import concurrent.futures  # Importing concurrent futures for multithreading

directory = 'documents_separated'
nltk.download('stopwords')
stemmer = snowballstemmer.stemmer('english')

def add_unique_key_value(data, key, value):
    if key not in data:
        data[key] = {value}
    else:
        data[key].add(value)

def remove_punctuation_from_tokens(tokens):
    translator = str.maketrans('', '', string.punctuation)
    tokens = [token.translate(translator) for token in tokens]
    return [token for token in tokens if token]

def tokenize(sentence):
    sentence = sentence.replace("\n", " ")
    sentence = sentence.lower()
    tokens = sentence.split(" ")
    tokens = remove_punctuation_from_tokens(tokens)
    tokens = stemmer.stemWords(tokens)
    filtered_words = [word for word in tokens if word not in stopwords.words('english')]
    return filtered_words

def process_file(filename):
    """Function to process a single file and return a dictionary of tokens."""
    token_dict = {}
    document_id = os.path.splitext(filename)[0]

    file_path = os.path.join(directory, filename)
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        content = file.read()

    tokens = tokenize(content)

    for token in tokens:
        add_unique_key_value(token_dict, token, document_id)

    return token_dict

# Main function to run the multithreading process
def main():
    all_token_dicts = []  # List to store token dictionaries from each file
    filenames = [filename for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]
    total_files = len(filenames)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a future for each file in the directory
        futures = {executor.submit(process_file, filename): filename for filename in filenames}

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            filename = futures[future]
            try:
                token_dict = future.result()  # Get the result from the future
                all_token_dicts.append(token_dict)  # Store the result
                print(f"Processed file: {filename} DONE")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

            # Print progress
            print(f"Processed ({i + 1} / {total_files}) documents")

    # Merge all token dictionaries into a single dictionary
    final_token_dict = {}
    for token_dict in all_token_dicts:
        for token, doc_ids in token_dict.items():
            add_unique_key_value(final_token_dict, token, doc_ids)

    # Save the final token dictionary to a JSON file
    with open('token_dict2.json', 'w') as json_file:
        json.dump({k: list(v) for k, v in final_token_dict.items()}, json_file)  # Convert sets to lists for JSON compatibility

    print("!!!!!!!!!!!!!!!DONE!!!!!!!!!!!!!!")
    print("token_dict has been saved to token_dict.json.")

if __name__ == "__main__":
    main()
