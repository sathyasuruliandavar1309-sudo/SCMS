from datetime import date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

from database import (
    init_db, fetch_all, fetch_one, execute,
    add_attendance, get_attendance,
    add_complaint, get_complaints,
    add_leave, get_leaves, update_leave_status,
    get_dashboard_stats,
)

app = Flask(__name__, template_folder="AI/templates", static_folder="AI/static")
app.secret_key = "change-this-demo-secret-key-before-deployment"

init_db()

QUIZ_QUESTIONS = [
    {"question": "Which keyword is used to define a function in Python?",
     "options": ["function", "def", "fun", "define"], "answer": "def"},
    {"question": "Which HTML tag creates a hyperlink?",
     "options": ["<link>", "<a>", "<href>", "<url>"], "answer": "<a>"},
    {"question": "Which SQL command retrieves data from a table?",
     "options": ["GET", "OPEN", "SELECT", "FETCH TABLE"], "answer": "SELECT"},
    {"question": "Which language is commonly used to style web pages?",
     "options": ["CSS", "SQL", "Python only", "Bash"], "answer": "CSS"},
    {"question": "What does CPU stand for?",
     "options": ["Central Processing Unit", "Computer Personal Unit",
                 "Central Program Utility", "Control Processing User"], "answer": "Central Processing Unit"},
]

EVENTS = [
    {"date": "2026-10-20", "title": "Innovation and Project Expo", "venue": "Main Auditorium",
     "description": "Showcase student projects, prototypes and creative ideas."},
    {"date": "2026-10-24", "title": "Coding Challenge", "venue": "Computer Lab",
     "description": "A friendly programming challenge for students."},
    {"date": "2026-10-30", "title": "Technical Seminar", "venue": "Seminar Hall",
     "description": "Student-focused talks on emerging technology."},
]
BUSES = [
    {"number": "Bus 2", "route": "Metupalayam → SRIET", "time": "7:30 AM", "status": "Scheduled"},
    {"number": "Bus 3", "route": "Gandhipuram → SRIET", "time": "8:00 AM", "status": "Scheduled"},
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    return redirect(url_for("dashboard" if session.get("logged_in") else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            session["username"] = username
            flash("Welcome to Smart Class 360.", "success")
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    stats = get_dashboard_stats()
    latest_attendance = fetch_all("SELECT * FROM attendance ORDER BY id DESC LIMIT 5")
    latest_tickets = fetch_all("SELECT * FROM maintenance_tickets ORDER BY id DESC LIMIT 5")
    return render_template("dashboard.html", stats=stats,
                           latest_attendance=latest_attendance, latest_tickets=latest_tickets)


@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():
    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        reg_no = request.form.get("register_number", "").strip()
        department = request.form.get("department", "").strip()
        status = request.form.get("status", "Present")
        if name and reg_no and department and status in ("Present", "Absent"):
            add_attendance(name, reg_no, department, str(date.today()), status)
            flash("Attendance record saved.", "success")
            return redirect(url_for("attendance"))
        flash("Please fill in all attendance details.", "error")
    return render_template("attendance.html", records=get_attendance(), today=str(date.today()))


@app.route("/bus")
@login_required
def bus():
    return render_template("bus.html", buses=BUSES)


@app.route("/events")
@login_required
def events():
    return render_template("events.html", events=EVENTS)


@app.route("/complaints", methods=["GET", "POST"])
@login_required
def complaints():
    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        reg_no = request.form.get("register_number", "").strip()
        category = request.form.get("category", "").strip()
        complaint_text = request.form.get("complaint", "").strip()
        if all([name, reg_no, category, complaint_text]):
            add_complaint(name, reg_no, category, complaint_text, str(date.today()))
            flash("Your report has been submitted.", "success")
            return redirect(url_for("complaints"))
        flash("Please complete every complaint field.", "error")
    return render_template("complaints.html", records=get_complaints())


@app.route("/complaints/status/<int:complaint_id>/<status>", methods=["POST"])
@login_required
def complaint_status(complaint_id, status):
    if status not in ("Pending", "In Progress", "Resolved"):
        flash("Invalid complaint status.", "error")
    else:
        execute("UPDATE complaints SET status=? WHERE id=?", (status, complaint_id))
        flash("Complaint status updated.", "success")
    return redirect(url_for("complaints"))


@app.route("/leave", methods=["GET", "POST"])
@login_required
def leave():
    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        reg_no = request.form.get("register_number", "").strip()
        department = request.form.get("department", "").strip()
        leave_date = request.form.get("leave_date", "").strip()
        reason = request.form.get("reason", "").strip()
        if all([name, reg_no, department, leave_date, reason]):
            add_leave(name, reg_no, department, leave_date, reason)
            flash("Leave request submitted.", "success")
            return redirect(url_for("leave"))
        flash("Please complete every leave field.", "error")
    return render_template("leave.html", records=get_leaves())


@app.route("/update-leave/<int:leave_id>/<status>", methods=["POST"])
@login_required
def update_leave(leave_id, status):
    if status not in ("Approved", "Rejected"):
        flash("Invalid leave status.", "error")
    else:
        update_leave_status(leave_id, status)
        flash(f"Leave request {status.lower()}.", "success")
    return redirect(url_for("leave"))


@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    if request.method == "POST":
        reg = request.form.get("register_number", "").strip()
        name = request.form.get("name", "").strip()
        dept = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        email = request.form.get("email", "").strip()
        if all([reg, name, dept, year]):
            try:
                execute("""INSERT INTO students(register_number,name,department,year,email)
                           VALUES(?,?,?,?,?)""", (reg, name, dept, year, email))
                flash("Student added successfully.", "success")
            except Exception:
                flash("Register number already exists or the details are invalid.", "error")
        else:
            flash("Register number, name, department and year are required.", "error")
        return redirect(url_for("students"))
    records = fetch_all("SELECT * FROM students ORDER BY department, name")
    return render_template("students.html", records=records)


@app.route("/class-monitor")
@login_required
def class_monitor():
    return render_template("class_monitor.html")


@app.route("/learning")
@login_required
def learning():
    materials = fetch_all("SELECT * FROM learning_materials ORDER BY subject, title")
    return render_template("learning.html", materials=materials)


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        reg = request.form.get("register_number", "").strip()
        if not name or not reg:
            flash("Enter student name and register number before submitting.", "error")
            return redirect(url_for("quiz"))
        score = 0
        for index, question in enumerate(QUIZ_QUESTIONS):
            if request.form.get(f"q{index}") == question["answer"]:
                score += 1
        execute("""INSERT INTO quiz_results(student_name,register_number,score,total,quiz_date)
                   VALUES(?,?,?,?,?)""", (name, reg, score, len(QUIZ_QUESTIONS), str(date.today())))
        return render_template("quiz_result.html", score=score, total=len(QUIZ_QUESTIONS),
                               name=name, reg=reg)
    history = fetch_all("SELECT * FROM quiz_results ORDER BY id DESC LIMIT 10")
    return render_template("quiz.html", questions=QUIZ_QUESTIONS, history=history)


@app.route("/maintenance", methods=["GET", "POST"])
@login_required
def maintenance():
    if request.method == "POST":
        reporter = request.form.get("reporter_name", "").strip()
        location = request.form.get("location", "").strip()
        equipment = request.form.get("equipment", "").strip()
        description = request.form.get("description", "").strip()
        if all([reporter, location, equipment, description]):
            execute("""INSERT INTO maintenance_tickets
                       (reporter_name,location,equipment,description,reported_date,status)
                       VALUES(?,?,?,?,?,'Pending')""",
                    (reporter, location, equipment, description, str(date.today())))
            flash("Maintenance ticket created.", "success")
            return redirect(url_for("maintenance"))
        flash("Please fill all maintenance fields.", "error")
    records = fetch_all("SELECT * FROM maintenance_tickets ORDER BY id DESC")
    return render_template("maintenance.html", records=records)


@app.route("/maintenance/status/<int:ticket_id>/<status>", methods=["POST"])
@login_required
def maintenance_status(ticket_id, status):
    if status not in ("Pending", "In Progress", "Resolved"):
        flash("Invalid ticket status.", "error")
    else:
        execute("UPDATE maintenance_tickets SET status=? WHERE id=?", (status, ticket_id))
        flash("Maintenance status updated.", "success")
    return redirect(url_for("maintenance"))


@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        course = request.form.get("course", "").strip()
        rating = request.form.get("rating", type=int)
        comments = request.form.get("comments", "").strip()
        if name and course and rating in range(1, 6) and comments:
            execute("""INSERT INTO feedback(student_name,course,rating,comments,submitted_date)
                       VALUES(?,?,?,?,?)""", (name, course, rating, comments, str(date.today())))
            flash("Thank you. Your feedback has been recorded.", "success")
            return redirect(url_for("feedback"))
        flash("Please fill all fields and select a rating from 1 to 5.", "error")
    records = fetch_all("SELECT * FROM feedback ORDER BY id DESC LIMIT 20")
    return render_template("feedback.html", records=records)


@app.route("/analytics")
@login_required
def analytics():
    stats = get_dashboard_stats()
    attendance_by_dept = fetch_all("""
        SELECT department, COUNT(*) AS total,
        SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present
        FROM attendance GROUP BY department ORDER BY department
    """)
    quiz_summary = fetch_all("""
        SELECT student_name, register_number, score, total, quiz_date
        FROM quiz_results ORDER BY id DESC LIMIT 10
    """)
    ticket_summary = fetch_all("""
        SELECT status, COUNT(*) AS total FROM maintenance_tickets GROUP BY status
    """)
    return render_template("analytics.html", stats=stats,
                           attendance_by_dept=attendance_by_dept,
                           quiz_summary=quiz_summary, ticket_summary=ticket_summary)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
    
@app.route('/learning-mode')
def learning_mode():
    return render_template('learning_mode.html')