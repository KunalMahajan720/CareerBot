from unittest import result

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
import requests
from resume_parser import parse_resume
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, Column, Integer, Text, MetaData, TIMESTAMP
from datetime import datetime


# Load environment variables
load_dotenv()
print("API KEY LOADED:", os.getenv("LLAMA_API_KEY"))
print("API URL LOADED:", os.getenv("LLAMA_API_URL"))

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Download NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Database Setup
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)
metadata = MetaData()
 
# Chat Log Table
chat_log = Table('chat_log', metadata,
    Column('ChatID', Integer, primary_key=True, autoincrement=True),            
    Column('UserID', Integer, nullable=True),
    Column('Message', Text, nullable=False),
    Column('Response', Text, nullable=False),
    Column('Sender', Text),
    Column('timestamp', TIMESTAMP, default=datetime.now)
)
 
# Resume Parse Table
resume_parse = Table('Resume_Parse', metadata,
    Column('ResumeID', Integer, primary_key=True, autoincrement=True),
    Column('UserID', Integer, nullable=True),
    Column('ResumeName', Text),
    Column('Email', Text),
    Column('Phone', Text),
    Column('Skills', Text),
    Column('ResumeURL', Text),
    Column('UploadedAt', TIMESTAMP, default=datetime.now)
)
 
# Create tables if not exist
metadata.create_all(engine)
 
# Helper function to save chat
 
def save_chat_to_db(user_message, bot_response):
    try:
        with engine.begin() as connection:
            connection.execute(
                chat_log.insert().values(
                    Message=user_message,
                    Response=bot_response,
                    Sender='bot',
                    timestamp=datetime.now()
                )
            )
        print("✅ Chat saved successfully.")
    except Exception as e:
        print(f"❌ Error saving chat to database: {e}")
 
# Helper function to save resume data
def save_parsed_resume(data, file_path, filename, user_id=None):
    try:
        with engine.begin() as conn:
            conn.execute(
                resume_parse.insert().values(
                    UserID=user_id,
                    ResumeName=filename,
                    Email=data.get("email"),
                    Phone=data.get("phone"),
                    Skills=", ".join(data.get("skills", [])) if isinstance(data.get("skills"), list) else data.get("skills"),
                    ResumeURL=file_path,
                    UploadedAt=datetime.now()
                )
            )
        print("✅ Resume data saved successfully.")
    except Exception as e:
        print(f"❌ Error saving resume data: {e}")

# Load ML model components
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

# Load and flatten structured knowledge base
try:
    with open("knowledgebase/dialogflow_qa_export.json", "r", encoding="utf-8") as f:
        grouped_kb = json.load(f)

    kb_flat = []
    for section_items in grouped_kb.values():
        kb_flat.extend(section_items)

    fallback_context = "\n".join([
        ", ".join(f"{k}: {v}" for k, v in item.items())
        for item in kb_flat
    ])
except Exception as e:
    kb_flat = []
    fallback_context = ""
    print(f"Error loading structured knowledge base: {e}")

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

# Search relevant context from flat list
def find_relevant_context_from_flat_kb(query):
    query = query.lower()
    matches = []
    for item in kb_flat:
        for value in item.values():
            if query in str(value).lower():
                matches.append(item)
                break
    if matches:
        return "\n".join([", ".join(f"{k}: {v}" for k, v in match.items()) for match in matches])
    return ""

# Llama 3 via openrouter.ai (Chat Completion Format)
import time
MODELS = [
    "openrouter/free",                              # auto-picks best available free model
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free"
]

def get_answer_from_context(question, context):
    try:
        llama_url = os.getenv("LLAMA_API_URL")
        llama_key = os.getenv("LLAMA_API_KEY")
        headers = {
            "Authorization": f"Bearer {llama_key}",
            "Content-Type": "application/json"
        }
        for model in MODELS:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that answers user questions using career, job, and course-related knowledge."},
                    {"role": "user", "content": f"{question}\n\nRelevant Information:\n{context}"}
                ],
                "max_tokens": 400
            }
            response = requests.post(llama_url, headers=headers, json=payload)
            result = response.json()
            print(f"Tried model: {model} → {result}")  # debug
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            time.sleep(1)  # wait 1 sec before trying next model
        return "I'm currently busy, please try again in a moment."
    except Exception as e:
        return f"API error: {str(e)}"

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
                # Save chat to database
                save_chat_to_db(message, response)
                return jsonify({"response": response})
    else:
        context = find_relevant_context_from_flat_kb(message)
        if not context:
            context = fallback_context
        try:
            answer = get_answer_from_context(message, context)
            # Save chat to database
            save_chat_to_db(message, answer)
            return jsonify({"response": answer})
        except Exception as e:
            return jsonify({"response": f"QA model error: {str(e)}"})


if __name__ == '__main__':
    app.run(debug=True)
