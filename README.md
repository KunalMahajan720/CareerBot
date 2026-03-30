# 🤖 CareerBot — Hybrid NLP Career Guidance Chatbot

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3.2-black?style=flat-square&logo=flask)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.8.0-orange?style=flat-square&logo=scikit-learn)
![NLTK](https://img.shields.io/badge/NLTK-3.9-green?style=flat-square)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?style=flat-square&logo=mysql)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter%20API-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> A production-ready, hybrid AI chatbot that combines a **Multinomial Naive Bayes classifier** for fast intent recognition with a **Large Language Model (LLaMA 3 / Gemini)** fallback for complex queries — built for career guidance, job search assistance, and resume analysis.

---

## 📸 Demo

![CareerBot Demo](assets/demo.png)

> *CareerBot in action — handling job search, resume upload, and career Q&A*

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Hybrid NLP Engine** | ML classifier (fast) + LLM fallback (smart) |
| 📄 **Resume Parser** | Extracts email, phone, skills from PDF/DOCX |
| 📊 **ATS Score** | Rates resume against job market keywords |
| 💬 **20+ Intent Categories** | Job search, interviews, salary, networking & more |
| 🗄️ **Chat Logging** | All conversations saved to MySQL database |
| 🔄 **Multi-Model Fallback** | Auto-switches LLM if one is rate-limited |
| 🌐 **REST API** | Clean Flask API with CORS support |

---

## 🏗️ Architecture

```
User Message
     │
     ▼
NLP Pre-processing  (NLTK tokenize → lemmatize → clean)
     │
     ▼
Naive Bayes Classifier
     │
     ├── Confidence > 30% ──► Match Intent ──► Pre-defined Response ✅
     │
     └── Confidence ≤ 30% ──► Knowledge Base Search
                                    │
                                    ├── Context Found ──► LLM API ──► AI Response ✅
                                    └── No Context   ──► Full KB as context ──► LLM API ✅
                                    
Every response → Saved to MySQL (chat_log table)
```

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-CORS
- **NLP:** NLTK (tokenization, lemmatization), Scikit-learn (Multinomial Naive Bayes, CountVectorizer)
- **LLM:** OpenRouter API (LLaMA 3.3 70B, Gemini 2.0 Flash, Mistral — with auto-fallback)
- **Database:** MySQL 8.0 + SQLAlchemy ORM
- **Resume Parsing:** pdfminer.six (PDF), docx2txt (DOCX)
- **Config:** python-dotenv

---

## 📁 Project Structure

```
CareerBot/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── train.py                # Model training script
│   ├── resume_parser.py        # Resume parsing & ATS scoring
│   ├── kb_processor.py         # Knowledge base processor
│   ├── intents.json            # Intent patterns & responses
│   ├── model.pkl               # Trained Naive Bayes model
│   ├── vectorizer.pkl          # CountVectorizer
│   ├── classes.pkl             # Intent class labels
│   ├── words.pkl               # Vocabulary
│   ├── chatbot.sql             # MySQL database schema & seed data
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variable template
│   ├── knowledgebase/          # Structured Q&A knowledge base (JSON)
│   ├── static/                 # CSS, JS frontend assets
│   ├── templates/              # HTML templates (Jinja2)
│   └── uploads/                # Uploaded resume storage
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- OpenRouter API Key → [Get one free here](https://openrouter.ai/keys)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/careerbot.git
cd careerbot/backend
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up the database
```bash
mysql -u root -p -e "CREATE DATABASE chatbot_db;"
mysql -u root -p chatbot_db < chatbot.sql
```

### 5. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
```dotenv
LLAMA_API_URL=https://openrouter.ai/api/v1/chat/completions
LLAMA_API_KEY=sk-or-v1-your-key-here
DB_URL=mysql+pymysql://root:yourpassword@localhost:3306/chatbot_db
```

### 6. Train the model
```bash
python train.py
```

### 7. Run the application
```bash
python app.py
```

Visit → **http://127.0.0.1:5000**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve chat UI |
| `POST` | `/chat` | Send message, get response |
| `POST` | `/upload_resume` | Upload & parse resume |

### Example `/chat` request:
```json
POST /chat
{
  "message": "I want a job in data science"
}
```
```json
Response:
{
  "response": "Sure! Please tell me your preferred job title or location."
}
```

---

## 🗃️ Database Schema

| Table | Purpose |
|---|---|
| `chat_log` | Stores all user messages and bot responses |
| `Resume_Parse` | Stores parsed resume data (email, phone, skills) |
| `jobs` | Job listings |
| `internships` | Internship listings |
| `applications` | Job/internship applications |

---

## 🤖 Supported Intent Categories

`greeting` · `job_search` · `apply_job` · `upload_resume` · `interview_tips` · `internships` · `resume_tips` · `contact_support` · `job_alerts` · `salary_negotiation` · `company_research` · `job_market_trends` · `networking` · `skills_development` · `job_fairs` · `freelancing` · `work_life_balance` · `career_growth` · `goodbye` · `thanks`

---

## 📊 Resume Parser Output

```json
{
  "email": "user@example.com",
  "phone": "9876543210",
  "skills": ["python", "sql", "machine learning"],
  "ats_score": 75,
  "suggestions": "Add SQL to strengthen your profile."
}
```

---

## 🚀 Retrain the Model

If you add new intents to `intents.json`, retrain the model:
```bash
python train.py
```
This regenerates `model.pkl`, `vectorizer.pkl`, `classes.pkl`, and `words.pkl`.

---

## ⚠️ Known Limitations

- Free LLM models on OpenRouter may be rate-limited during peak hours (auto-fallback handles this)
- Resume parser currently detects a predefined skill set — extend `extract_skills()` in `resume_parser.py` to add more
- Marathi and other regional languages fall through to the LLM layer (classifier is English-only)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Kunal Mahajan**  
📧 kunalmahajan2499@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)

---

> ⭐ If you found this project helpful, please consider giving it a star!
