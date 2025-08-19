# backend/modules/ai/auto_tagging.py

import spacy
from collections import Counter

# Load a pre-trained NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def auto_tag(text):
    """
    Analyzes text and suggests relevant tags based on named entities and keywords.
    """
    doc = nlp(text)
    tags = []

    # Extract named entities
    for ent in doc.ents:
        tags.append(ent.text.lower())

    # Extract nouns and proper nouns as potential keywords
    keywords = [token.text.lower() for token in doc if token.pos_ in ("NOUN", "PROPN")]
    tags.extend(keywords)

    # Simple frequency-based filtering
    tag_counts = Counter(tags)
    
    # Filter for tags that appear more than once or are part of named entities
    filtered_tags = [tag for tag, count in tag_counts.items() if count > 1 or tag in [ent.text.lower() for ent in doc.ents]]

    return list(set(filtered_tags))