import re
import pdfplumber
import PyPDF2
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------- CLEAN --------
def clean_text(text):
    text = text.lower()
    text = text.replace("c++", "cplusplus").replace("power bi", "powerbi")
    text = re.sub(r'[^a-z0-9\s@.+-]', ' ', text)
    return text

def extract_name(text, filename):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    invalid_words = ['resume', 'cv', 'objective', 'summary', 'profile', 'experience', 'education', 'skills', 'projects', 'certifications', 'github', 'linkedin', 'portfolio', 'contact']
    
    for line in lines[:10]: # Check first 10 lines
        if any(x in line.lower().split() for x in invalid_words):
            continue
            
        clean_line = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', line)
        clean_line = re.sub(r'email\s*:?', '', clean_line, flags=re.IGNORECASE)
        clean_line = re.sub(r'mobile\s*:?', '', clean_line, flags=re.IGNORECASE)
        clean_line = re.sub(r'phone\s*:?', '', clean_line, flags=re.IGNORECASE)
        clean_line = re.sub(r'\+?\d[\d -]{8,12}\d', '', clean_line)
        clean_line = re.sub(r'(https?://[^\s]+)', '', clean_line)
        clean_line = re.sub(r'www\.[^\s]+', '', clean_line)
        clean_line = re.sub(r'[^\s]+@[^\s]+', '', clean_line) # catch remaining emails
        clean_line = re.sub(r'[^a-zA-Z\s]', '', clean_line) # remove non-alphabetic
        
        clean_line = ' '.join(clean_line.split())
        
        if 2 < len(clean_line) < 40 and 1 <= len(clean_line.split()) <= 4:
            return clean_line.title()
    
    # Fallback to filename
    clean_filename = filename.rsplit('.', 1)[0].replace('_', ' ') if '.' in filename else filename.replace('_', ' ')
    return clean_filename.title()

# -------- PDF TEXT (FIXED) --------
def extract_text(file):
    text = ""

    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t
    except:
        pass

    if not text.strip():
        try:
            file.seek(0)
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t
        except:
            pass

    return clean_text(text)

# -------- SCORE --------
def calculate_score(resume_text, job_desc):
    tfidf = TfidfVectorizer(stop_words='english')
    mat = tfidf.fit_transform([resume_text, job_desc])
    return cosine_similarity(mat[0:1], mat[1:2])[0][0]

# -------- SKILLS --------
import json
import os

SKILL_BANK = []
try:
    skills_file_path = os.path.join(os.path.dirname(__file__), 'skills.json')
    with open(skills_file_path, 'r', encoding='utf-8') as f:
        skills_data = json.load(f)
        for category, skills in skills_data.items():
            SKILL_BANK.extend(skills)
except Exception as e:
    print(f"Error loading skills.json: {e}")

def extract_skills(job_desc):
    jd = clean_text(job_desc)
    # Use word boundaries so we don't match 'excel' inside 'excellent'
    return [s for s in SKILL_BANK if re.search(r'\b' + re.escape(s) + r'\b', jd)]

def match_skills(text, skills):
    return [s for s in skills if re.search(r'\b'+re.escape(s)+r'\b', text)]

# -------- EXPERIENCE --------
def get_experience_years(text):
    matches = re.findall(r'(20\d{2}).{1,25}?(20\d{2}|present)', text)
    total = 0
    current_year = datetime.now().year

    for start, end in matches:
        start = int(start)
        end = current_year if end.lower() == "present" else int(end)

        if end > start:
            total += (end - start)

    return total

def extract_req_experience(job_desc):
    jd = clean_text(job_desc)
    # look for 'x years' or 'x+ years'
    matches = re.findall(r'(\d+)\+?\s*years?', jd)
    if matches:
        # filter out unrealistic numbers (like 2023 years)
        valid = [int(m) for m in matches if int(m) < 30]
        if valid:
            return min(valid) # usually looking for minimum required
    return 0

# -------- CONTACT --------
def extract_email(text):
    m = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    return m[0] if m else "Not found"

def extract_phone(text):
    # Match sequences of digits, spaces, and hyphens that have at least 9 digits
    matches = re.findall(r'\+?\d[\d\s\-]{7,}\d', text)
    for match in matches:
        digits = re.sub(r'\D', '', match)
        if len(digits) >= 9 and len(digits) <= 15:
            return match.strip()
    return "Not found"

# -------- FILTER --------
def apply_filters(candidate, filters):

    if candidate["experience"] < filters.get("min_exp", 0):
        return False

    if candidate["percent"] < filters.get("min_percent", 0):
        return False

    must = filters.get("must_have", [])
    if must:
        text = candidate["raw_text"]
        for s in must:
            if not re.search(r'\b'+re.escape(s)+r'\b', text):
                return False

    return True