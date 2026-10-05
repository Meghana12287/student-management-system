import sqlite3
from functools import wraps

from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash

from database import get_db, init_db

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # change before deploying
init_db()

COURSES = ["Computer Science", "Mechanical", "Electronics", "Civil",
           "Business Admin", "Mathematics"]
STATUSES = ["Active", "Inactive", "Graduated"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def read_form():
    f = request.form
    gpa = f.get("gpa", "").strip()
    return {
        "roll_no": f.get("roll_no", "").strip().upper(),
        "name": f.get("name", "").strip(),
        "email": f.get("email", "").strip(),
        "phone": f.get("phone", "").strip(),
        "course": f.get("course", ""),
        "year": int(f.get("year") or 1),
        "gpa": float(gpa) if gpa else None,
        "status": f.get("status", "Active"),
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?",
                            (request.form["username"].strip(),)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], request.form["password"]):
            session["user"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Wrong username or password. Try again.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    conn = get_db()
    stats = {
        "total": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "active": conn.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0],
        "graduated": conn.execute("SELECT COUNT(*) FROM students WHERE status='Graduated'").fetchone()[0],
        "avg_gpa": conn.execute("SELECT ROUND(AVG(gpa),2) FROM students WHERE gpa IS NOT NULL").fetchone()[0] or 0,
    }
    by_course = conn.execute(
        "SELECT course, COUNT(*) AS n FROM students GROUP BY course ORDER BY n DESC").fetchall()
    recent = conn.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    top = max([r["n"] for r in by_course], default=1)
    return render_template("dashboard.html", stats=stats, by_course=by_course,
                           recent=recent, top=top)


@app.route("/students")
@login_required
def students():
    q = request.args.get("q", "").strip()
    course = request.args.get("course", "")
    sql, params = "SELECT * FROM students WHERE 1=1", []
    if q:
        sql += " AND (name LIKE ? OR roll_no LIKE ? OR email LIKE ?)"
        params += [f"%{q}%"] * 3
    if course:
        sql += " AND course = ?"
        params.append(course)
    sql += " ORDER BY name"
    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template("students.html", students=rows, q=q,
                           course=course, courses=COURSES)


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        data = read_form()
        try:
            conn = get_db()
            conn.execute("""INSERT INTO students (roll_no, name, email, phone, course, year, gpa, status)
                            VALUES (:roll_no,:name,:email,:phone,:course,:year,:gpa,:status)""", data)
            conn.commit()
            conn.close()
            flash(f"{data['name']} was added.", "success")
            return redirect(url_for("students"))
        except sqlite3.IntegrityError:
            conn.close()
            flash(f"Roll number {data['roll_no']} already exists. Use a different one.", "error")
        return render_template("form.html", s=data, courses=COURSES, statuses=STATUSES, mode="Add")
    return render_template("form.html", s={}, courses=COURSES, statuses=STATUSES, mode="Add")


@app.route("/students/<int:sid>/edit", methods=["GET", "POST"])
@login_required
def edit_student(sid):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    if not student:
        conn.close()
        flash("Student not found.", "error")
        return redirect(url_for("students"))
    if request.method == "POST":
        data = read_form()
        data["id"] = sid
        try:
            conn.execute("""UPDATE students SET roll_no=:roll_no, name=:name, email=:email,
                            phone=:phone, course=:course, year=:year, gpa=:gpa, status=:status
                            WHERE id=:id""", data)
            conn.commit()
            conn.close()
            flash("Changes saved.", "success")
            return redirect(url_for("students"))
        except sqlite3.IntegrityError:
            flash(f"Roll number {data['roll_no']} already exists. Use a different one.", "error")
            student = data
    conn.close()
    return render_template("form.html", s=student, courses=COURSES, statuses=STATUSES, mode="Edit")


@app.route("/students/<int:sid>/delete", methods=["POST"])
@login_required
def delete_student(sid):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (sid,))
    conn.commit()
    conn.close()
    flash("Student deleted.", "success")
    return redirect(url_for("students"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
