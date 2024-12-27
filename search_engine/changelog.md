# app.py
- Simple search engine with boolean search

# app_v2
- Added TF-IDF Rank

# app_v3
- Added positional search feature for query with more than 1 word

# app_v4
- Fixed TF-IDF Rank

# app_v5
- Fixed query bug where unwanted characters (\&^%$#@!*) etc are present

# app_v6
- Updated UI for homepage and results page

# app_v7
- Added auto suggest when typing

# app_v8
- Added auto correct feature using Levenshtein distance

# app_v9
- Updated UI for each document
- Fixed UI for auto-suggest
- Fixed UI & link for auto-correct

# app_v10
- Refined autocorrect behavior: If the searched word exists in >= 10 documents, suppress the "Did you mean..." suggestion to avoid unnecessary corrections
- Added "About x results" on results page

# app_v11


## To Do
- Implement wildcard query functionality to allow more flexible search patterns
- Enhance autosuggest functionality to handle multi-word inputs: Ensure that suggested sentences are verified to exist in the dataset before being displayed
- Revamp the pagination UI to make navigation between pages more intuitive and visually appealing
- Implement a back button on document pages that seamlessly returns users to their previous search results, preserving filters and states
- Redesign the UI for auto-suggestions to improve clarity and user experience
- Upgrade the UI for individual document views to provide a modern and more user-friendly presentation
- Add a night mode option
