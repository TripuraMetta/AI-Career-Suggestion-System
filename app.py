from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import sqlite3
import os
import re
from datetime import datetime

# Try to import python-docx for resume parsing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

app = Flask(__name__)

# ─── Database Setup ────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect('career.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            skills    TEXT    NOT NULL,
            field     TEXT    NOT NULL,
            best_career TEXT  NOT NULL,
            confidence REAL   NOT NULL,
            all_careers TEXT  NOT NULL,
            top3      TEXT    NOT NULL,
            timestamp TEXT    NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ─── Dataset Loading ───────────────────────────────────────────────────────────

def load_dataset():
    with open('dataset.json', 'r') as f:
        return json.load(f)['careers']

# ─── Skill Extraction from Resume ─────────────────────────────────────────────

def extract_text_from_docx(filepath):
    if not DOCX_AVAILABLE:
        return ""
    doc = Document(filepath)
    return ' '.join([para.text for para in doc.paragraphs])

def extract_skills_from_text(text, dataset):
    text_lower = text.lower()
    found_skills = []
    all_skills = set()
    for career in dataset:
        for skill in career['skills']:
            all_skills.add(skill.lower())
    for skill in all_skills:
        # Use word boundary matching for short skills, substring for longer
        if len(skill) <= 3:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        else:
            if skill in text_lower:
                found_skills.append(skill)
    return list(set(found_skills))

# ─── Career Matching Algorithm ─────────────────────────────────────────────────

def predict_careers(user_skills, dataset):
    user_skills_lower = [s.strip().lower() for s in user_skills]
    scores = []

    for career in dataset:
        career_skills = [s.lower() for s in career['skills']]
        matched = [s for s in user_skills_lower if s in career_skills]
        score = len(matched)
        if score > 0:
            confidence = round((score / len(career_skills)) * 100, 1)
            scores.append({
                'field': career['field'],
                'roles': career['roles'],
                'matched_skills': matched,
                'score': score,
                'confidence': confidence
            })

    scores.sort(key=lambda x: (x['score'], x['confidence']), reverse=True)

    if not scores:
        return None

    best = scores[0]
    top3 = scores[:3]
    all_careers = scores

    return {
        'field': best['field'],
        'best_career': best['roles'][0] if best['roles'] else 'N/A',
        'confidence': best['confidence'],
        'all_careers': all_careers,
        'top3': top3,
        'matched_skills': best['matched_skills']
    }

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
def predict():
    name = request.form.get('name', '').strip()
    skills_input = request.form.get('skills', '').strip()
    resume = request.files.get('resume')

    dataset = load_dataset()
    user_skills = []
    source = 'manual'

    # Resume upload path
    if resume and resume.filename.endswith('.docx'):
        upload_path = os.path.join('uploads', resume.filename)
        os.makedirs('uploads', exist_ok=True)
        resume.save(upload_path)
        text = extract_text_from_docx(upload_path)
        user_skills = extract_skills_from_text(text, dataset)
        source = 'resume'
        os.remove(upload_path)
    elif skills_input:
        user_skills = [s.strip() for s in skills_input.split(',') if s.strip()]

    if not user_skills:
        return render_template('form.html', error="No skills could be detected. Please enter skills manually or upload a valid .docx resume.")

    result = predict_careers(user_skills, dataset)

    if not result:
        return render_template('form.html', error="No matching careers found for the provided skills. Try adding more relevant technical skills.")

    # Store in DB
    conn = get_db()
    conn.execute('''
        INSERT INTO results (name, skills, field, best_career, confidence, all_careers, top3, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        ', '.join(user_skills),
        result['field'],
        result['best_career'],
        result['confidence'],
        json.dumps(result['all_careers']),
        json.dumps(result['top3']),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    conn.commit()
    conn.close()

    return render_template('result.html',
        name=name,
        skills=user_skills,
        result=result,
        source=source
    )

@app.route('/history')
def history():
    conn = get_db()
    rows = conn.execute('SELECT * FROM results ORDER BY id DESC').fetchall()
    conn.close()

    records = []
    for row in rows:
        records.append({
            'id': row['id'],
            'name': row['name'],
            'skills': row['skills'],
            'field': row['field'],
            'best_career': row['best_career'],
            'confidence': row['confidence'],
            'top3': json.loads(row['top3']),
            'timestamp': row['timestamp']
        })

    return render_template('history.html', records=records)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    conn = get_db()
    conn.execute('DELETE FROM results')
    conn.commit()
    conn.close()
    return redirect(url_for('history'))

# ─── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
