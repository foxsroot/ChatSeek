import json
from collections import defaultdict

# Define the end symbol for rotations
end_symbol = '$'


def generate_permuterm(term):
    """Generate all rotations of the term with an end symbol."""
    term_with_end = term + end_symbol
    return [term_with_end[i:] + term_with_end[:i] for i in range(len(term_with_end))]


def build_permuterm_index_from_dict(token_dict):
    """Build a permuterm index using an existing dictionary of terms."""
    permuterm_index = defaultdict(list)

    for term, document_data in token_dict.items():
        # Generate rotations for each term
        rotations = generate_permuterm(term)
        for rotation in rotations:
            # Store each rotation with references to documents
            permuterm_index[rotation].extend(document_data.keys())

    return permuterm_index


# Load the filtered token dictionary
with open('search_engine/token_dict_positional.json', 'r') as json_file:
    token_dict = json.load(json_file)

# Build permuterm index from the loaded dictionary
permuterm_index = build_permuterm_index_from_dict(token_dict)

# Save the permuterm index to a JSON file
with open('search_engine/perm_index.json', 'w') as json_file:
    json.dump(permuterm_index, json_file)

print("Permuterm index created and saved as 'perm_index.json'")
