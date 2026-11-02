# Smart Class 360 – Smart Campus Management System

A student-centred Smart Campus / Smart Classroom prototype built with Python, Flask, SQLite, HTML, CSS and JavaScript.

## Included modules
- Admin login and dashboard
- Attendance recording and attendance history
- Campus bus information
- Campus events
- Complaint reporting and status updates
- Leave requests and approve/reject actions
- Student directory
- Smart Learning resources
- Five-question Smart Quiz with score history
- Classroom equipment maintenance tickets
- Student feedback
- Basic classroom focus / mobile-learning guidance
- Dashboard analytics

## Requirements
- Python 3.10 or later
- pip

## Run in VS Code / PowerShell
1. Extract this ZIP.
2. Open the `Smart_Class_360` folder in VS Code.
3. Open Terminal and run:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python app.py
   ```

4. Open `http://127.0.0.1:5000` in your browser.

If PowerShell blocks activation, you can skip activation and run:
`python -m pip install -r requirements.txt` then `python app.py`.

## Demo login
- Username: `admin`
- Password: `admin123`

This is a college-project demonstration login. Before any real deployment, add secure password storage, user roles, CSRF protection, HTTPS and appropriate privacy controls.

## Database
The project starts with the supplied `campus(1).db` copied as `campus.db`, so the existing attendance, complaint and leave records are preserved. New tables are created automatically when the app starts. Keep `campus.db` in the same folder as `app.py`.

## Notes
- Quiz questions, campus events and bus information are sample/demo content and can be edited in `app.py` / templates.
- The class monitor page is a policy and learning-mode demo. It does not secretly access a camera or claim to identify students.
- The app uses SQLite and does not require MySQL.
