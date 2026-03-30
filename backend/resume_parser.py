import os
import re
import docx2txt
from pdfminer.high_level import extract_text

def extract_resume_text(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.pdf':
        return extract_text(file_path)
    elif ext == '.docx':
        return docx2txt.process(file_path)
    else:
        return ""

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r'\b\d{10}\b', text)
    return match.group(0) if match else "Not found"

def extract_skills(text):
    skills = ['python', 'java', 'sql', 'excel', 'machine learning', 'data analysis']
    found = [skill for skill in skills if skill in text.lower()]
    return found

def get_ats_score(skills_found):
    base_skills = ['python', 'sql', 'machine learning', 'data analysis']
    score = int((len([s for s in base_skills if s in skills_found]) / len(base_skills)) * 100)
    return score

def generate_suggestions(skills_found):
    suggestions = []
    if 'python' not in skills_found:
        suggestions.append("Consider learning Python.")
    if 'sql' not in skills_found:
        suggestions.append("Add SQL to strengthen your profile.")
    if 'machine learning' not in skills_found:
        suggestions.append("Machine learning can boost your career opportunities.")
    return " ".join(suggestions)

def parse_resume(file_path):
    text = extract_resume_text(file_path)
    skills = extract_skills(text)
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": skills,
        "ats_score": get_ats_score(skills),
        "suggestions": generate_suggestions(skills)
    }
