# ⚡ AI Career Suggestion System

A full-stack Flask web application that recommends career paths based on your skills or resume.

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

The SQLite database (`career.db`) is created automatically on first run.

---

## 📁 Folder Structure

```
AI-Career-Suggestion/
│
├── app.py                  ← Flask backend (routes, logic, DB)
├── dataset.json            ← Skills → Career Field → Roles mapping
├── career.db               ← SQLite database (auto-created)
├── requirements.txt
│
├── static/
│   ├── css/style.css       ← Custom CSS (dark theme)
│   └── js/validation.js    ← jQuery form validation & UI
│
└── templates/
    ├── home.html           ← Landing page
    ├── form.html           ← Skill input / resume upload
    ├── result.html         ← Career prediction results
    └── history.html        ← Past results from SQLite
```

---

## 🧠 How the Algorithm Works

1. User inputs skills (comma-separated) OR uploads a `.docx` resume
2. If resume: text is extracted and skills are detected by matching against `dataset.json`
3. Each career field is scored by how many user skills match its skill list
4. **Confidence** = `(matched_skills / total_field_skills) × 100`
5. Fields are ranked by score; top field = predicted career
6. Top 3 suggestions + all matches displayed
7. Result stored in SQLite `results` table

---

## 🗃️ Database Schema

**Table: `results`**

| Column       | Type    | Description                     |
|--------------|---------|---------------------------------|
| id           | INTEGER | Auto-increment primary key      |
| name         | TEXT    | User's name                     |
| skills       | TEXT    | Comma-separated skills list     |
| field        | TEXT    | Top predicted career field      |
| best_career  | TEXT    | Best matching job role          |
| confidence   | REAL    | Confidence percentage (0-100)   |
| all_careers  | TEXT    | JSON of all matched careers     |
| top3         | TEXT    | JSON of top 3 career matches    |
| timestamp    | TEXT    | Date/time of analysis           |

---

## 🛠️ Technologies

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Frontend   | HTML5, CSS3, Bootstrap 5, jQuery        |
| Backend    | Python 3, Flask                         |
| Database   | SQLite (via Python's built-in `sqlite3`)|
| Resume     | python-docx                             |
| Data       | JSON                                    |

---

## 🔮 Future Scope

- PDF resume support
- Login / user accounts
- Charts with Chart.js
- ML model (scikit-learn) for smarter predictions
- Deploy on Render / Railway / PythonAnywhere
