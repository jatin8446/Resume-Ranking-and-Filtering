import re
from utils import extract_text

def extract_name_test(text, filename):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    invalid_words = ['resume', 'cv', 'objective', 'summary', 'profile', 'experience', 'education', 'skills', 'projects', 'certifications', 'github', 'linkedin', 'portfolio', 'contact']
    
    for line in lines[:10]:
        if any(x in line.lower().split() for x in invalid_words):
            continue
            
        clean_line = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', line)
        clean_line = re.sub(r'email\s*:?', '', clean_line, flags=re.IGNORECASE)
        clean_line = re.sub(r'mobile\s*:?', '', clean_line, flags=re.IGNORECASE)
        clean_line = re.sub(r'phone\s*:?', '', clean_line, flags=re.IGNORECASE)
        clean_line = re.sub(r'\+?\d[\d -]{8,12}\d', '', clean_line)
        clean_line = re.sub(r'(https?://[^\s]+)', '', clean_line)
        clean_line = re.sub(r'www\.[^\s]+', '', clean_line)
        clean_line = re.sub(r'[^\s]+@[^\s]+', '', clean_line)
        clean_line = re.sub(r'[^a-zA-Z\s]', '', clean_line)
        
        clean_line = ' '.join(clean_line.split())
        
        if 2 < len(clean_line) < 40 and 1 <= len(clean_line.split()) <= 4:
            return clean_line.title()
            
    clean_filename = filename.rsplit('.', 1)[0].replace('_', ' ') if '.' in filename else filename.replace('_', ' ')
    return clean_filename.title()

with open('resumes/sourabh_bajaj_resume.pdf', 'rb') as f:
    text = extract_text(f)
    print(extract_name_test(text, 'sourabh_bajaj_resume.pdf'))
