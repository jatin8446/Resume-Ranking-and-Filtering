from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import random
from utils import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'resumes'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

stored_resumes = []
stored_texts = []
stored_job_desc = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    global stored_resumes, stored_texts, stored_job_desc

    results = []

    if request.method == 'POST':

        action = request.form.get("action")

        # ANALYZE
        if action == "analyze":
            stored_job_desc = request.form.get('job_desc', '')
            jd_pdf = request.files.get('jd_pdf')
            if jd_pdf and jd_pdf.filename != "":
                jd_text = extract_text(jd_pdf)
                stored_job_desc = stored_job_desc + "\n" + jd_text

            files = request.files.getlist('resume')

            has_files = any(f.filename != "" for f in files)
            
            if has_files:
                stored_resumes = []
                stored_texts = []

                for f in files:
                    if f.filename == "":
                        continue
                    filename = secure_filename(f.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    f.save(file_path)
                    
                    with open(file_path, "rb") as saved_file:
                        text = extract_text(saved_file)
                    
                    stored_resumes.append(filename)
                    stored_texts.append(text)

        if not stored_texts:
            return render_template('index.html', results=[])

        # 🔥 FILTER INPUTS
        raw_min_exp = request.form.get('min_exp', '')
        raw_min_percent = request.form.get('min_percent', '')
        min_exp = int(raw_min_exp) if raw_min_exp else 0
        min_percent = int(raw_min_percent) if raw_min_percent else 0

        must_have_raw = request.form.get('must_have', '')
        must_have = [s.strip().lower() for s in must_have_raw.split(',') if s.strip()]

        filters = {
            "min_exp": min_exp,
            "min_percent": min_percent,
            "must_have": must_have
        }

        job_desc_clean = clean_text(stored_job_desc)
        skills = extract_skills(stored_job_desc)
        
        # Ensure must-have skills are considered in scoring and displayed
        for s in must_have:
            if s not in skills:
                skills.append(s)

        for i in range(len(stored_texts)):
            text = stored_texts[i]
            name = stored_resumes[i]

            # 1. Keyword Relevance Score (10%)
            keyword_score = calculate_score(text, job_desc_clean) if stored_job_desc else 0
            keyword_percent = keyword_score * 100

            # 2. Skills Match Score (60%)
            matched = match_skills(text, skills)
            total = len(skills)
            skill_percent = (len(matched)/total)*100 if total else 0
            missing_skills = [s for s in skills if s not in matched]

            # 3. Experience Match Score (30%)
            candidate_exp = get_experience_years(text)
            required_exp = min_exp if min_exp > 0 else extract_req_experience(stored_job_desc)
            if required_exp > 0:
                exp_percent = min(100.0, (candidate_exp / required_exp) * 100.0)
            else:
                exp_percent = 100.0 # If no experience required, give full marks

            # Calculate Final Weighted Score
            if total > 0:
                percent = (skill_percent * 0.60) + (exp_percent * 0.30) + (keyword_percent * 0.10)
            else:
                # If no skills are defined, fall back to simple weighting
                percent = (exp_percent * 0.70) + (keyword_percent * 0.30)

            # Generate AI Explanation
            ai_explanation = []
            if matched:
                ai_explanation.append(f"✔ Strong match in skills: {', '.join(matched[:3])}")
            if missing_skills:
                ai_explanation.append(f"❌ Missing key skills: {', '.join(missing_skills[:3])}")
            if candidate_exp >= required_exp and required_exp > 0:
                exp_text = f"{candidate_exp} yrs" if candidate_exp > 0 else "Fresher"
                ai_explanation.append(f"✔ Experience meets requirement ({exp_text})")
            elif required_exp > 0:
                exp_text = f"{candidate_exp} yrs" if candidate_exp > 0 else "Fresher"
                ai_explanation.append(f"❌ Experience below requirement (Has {exp_text}, needs {required_exp} yrs)")

            # Generate Name
            clean_name = extract_name(text, name)
            
            candidate = {
                "name": clean_name,
                "filename": name,
                "percent": round(percent, 2),
                "experience": candidate_exp,
                "email": extract_email(text),
                "phone": extract_phone(text),
                "raw_text": text,
                "matched_skills": matched,
                "missing_skills": missing_skills,
                "ai_explanation": ai_explanation,
                "location": random.choice(["SF", "NYC", "Austin", "London", "Remote"])
            }

            if not apply_filters(candidate, filters):
                continue

            if percent >= 60:
                status = "SELECTED"
            elif percent >= 40:
                status = "CONSIDER"
            else:
                status = "REJECTED"

            candidate["status"] = status
            results.append(candidate)

        results = sorted(results, key=lambda x: x["percent"], reverse=True)

        total_resumes = len(stored_texts)
        total_processed = len(results)
        highest_score = results[0]["percent"] if results else 0
        selected_count = len([r for r in results if r['status'] == 'SELECTED'])
        consider_count = len([r for r in results if r['status'] == 'CONSIDER'])

        return render_template('index.html', 
                               results=results, 
                               total_resumes=total_resumes, 
                               total_processed=total_processed, 
                               highest_score=highest_score, 
                               selected_count=selected_count,
                               consider_count=consider_count,
                               job_desc=stored_job_desc,
                               min_exp=raw_min_exp,
                               min_percent=raw_min_percent,
                               must_have=must_have_raw)

    return render_template('index.html', results=[])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)