import nltk
nltk.download('punkt')
nltk.download('wordnet')

import json
import numpy as np
import random
import pickle
from nltk.stem import WordNetLemmatizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

lemmatizer = WordNetLemmatizer()

# Load intents file
with open('intents.json') as f:
    data = json.load(f)

words = []
classes = []
documents = []

# Tokenize and label patterns
for intent in data['intents']:
    for pattern in intent['patterns']:
        tokens = nltk.word_tokenize(pattern)
        lemmatized_tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens if w.isalpha()]
        words.extend(lemmatized_tokens)
        documents.append((" ".join(lemmatized_tokens), intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# Sort and deduplicate
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

