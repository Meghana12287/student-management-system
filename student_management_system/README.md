# Campus Register: Student Management System

A Flask + SQLite web app to manage student records.

## Features
- Admin login (session based, hashed password)
- Dashboard: totals, average GPA, students per course, recent additions
- Add, edit, delete students
- Search by name, roll number or email; filter by course
- Responsive layout (desktop and mobile)

## Run in VS Code
1. Open this folder in VS Code (File > Open Folder).
2. Open a terminal (Ctrl+`) and create a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Start the app: `python app.py` (or press F5)
5. Open http://127.0.0.1:5000

Login: **admin** / **admin123**

The database (`students.db`) is created automatically with sample students on first run.

## Structure
```
app.py            routes and app logic
database.py       SQLite setup and sample data
templates/        HTML pages (Jinja2)
static/css/       styles
.vscode/          VS Code debug config
```

Before deploying, change `app.secret_key` in app.py and the admin password.
