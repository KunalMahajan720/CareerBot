from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import nltk
import pickle
import json
import random
import numpy as np
import requests
from nltk.stem import WordNetLemmatizer
from resume_parser import parse_resume
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# NLTK setup
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model components
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("classes.pkl", "rb") as f:
        classes = pickle.load(f)
    with open("vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open("intents.json") as f:
        intents = json.load(f)
except Exception as e:
    print(f"Error loading model files: {e}")

# Load structured knowledge base
# Load structured knowledge base (questions and answers)
try:
    with open("knowledgebase/kb_processed.json", "r", encoding="utf-8") as f:
        kb_data = json.load(f)
    # Format for QA context (question: answer pairs)
    context_data = "\n".join([
        f"Q: {item.get('Question', '')} A: {item.get('Answer', '')}" for item in kb_data
    ])
except Exception as e:
    kb_data = []
    context_data = ""
    print(f"Error loading new KB: {e}")


lemmatizer = WordNetLemmatizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    parsed_data = parse_resume(file_path)
    return jsonify(parsed_data)

def get_llama_answer(question, context):
    try:
        llama_url = os.getenv("LLAMA_API_URL")
        llama_key = os.getenv("LLAMA_API_KEY")
        headers = {"Authorization": f"Bearer {llama_key}"}
        payload = {"question": question, "context": context}
        response = requests.post(llama_url, json=payload, headers=headers)
        result = response.json()
        return result.get("answer", "Sorry, I couldn't find an answer.")
    except Exception as e:
        return f"Llama API error: {str(e)}"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"response": "No message received."})

    tokens = nltk.word_tokenize(message)
    processed_tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens if w.isalpha()]
    cleaned_sentence = " ".join(processed_tokens)

    try:
        X_test = vectorizer.transform([cleaned_sentence]).toarray()
    except Exception as e:
        return jsonify({"response": f"Error processing input: {str(e)}"})

    probs = model.predict_proba(X_test)[0]
    top_index = np.argmax(probs)
    confidence = probs[top_index]

    if confidence > 0.3:
        intent_tag = classes[top_index]
        for intent in intents["intents"]:
            if intent["tag"] == intent_tag:
                response = random.choice(intent["responses"])
                return jsonify({"response": response})
    else:
        if context_data.strip():
            answer = get_llama_answer(message, context_data)
            return jsonify({"response": answer})
        else:
            return jsonify({"response": "I'm not sure how to respond to that. Can you try rephrasing?"})

if __name__ == '__main__':
    app.run(debug=True)
