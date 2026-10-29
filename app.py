"""
Placement & Internship Portal (Demo)
A lightweight Flask web application for testing and demonstration.
Uses Python built-in SQLite database - no external DB configuration required.
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dummy-secure-portal-demo-key"
DB_PATH = os.path.join(os.path.dirname(__file__), "placement.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        salary TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Pending Review',
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (job_id) REFERENCES jobs (id)
    )
    """)
    
    # Seed default users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("Placement Officer (Admin)", "admin@test.com", generate_password_hash("admin123"), "admin")
        )
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("Rahul Sharma (Student)", "student@test.com", generate_password_hash("student123"), "student")
        )

    # Seed sample jobs if empty
    cursor.execute("SELECT COUNT(*) FROM jobs")
    if cursor.fetchone()[0] == 0:
        sample_jobs = [
            ("Associate Software Engineer", "TechNova Solutions", "Bangalore / Hybrid", "INR 12 - 15 LPA", "Responsible for developing backend REST APIs using Python and modern cloud microservices."),
            ("Data Analyst Intern", "Quantum Insights Labs", "Hyderabad / Remote", "INR 40,000 / month", "Work with SQL, Python pandas, and dashboarding tools to deliver business intelligence reports."),
            ("Frontend Developer", "Apex Digital", "Chennai / On-site", "INR 9 - 11 LPA", "Build responsive user interfaces using HTML5, CSS3, modern JavaScript, and component libraries.")
        ]
        cursor.executemany(
            "INSERT INTO jobs (title, company, location, salary, description) VALUES (?, ?, ?, ?, ?)",
            sample_jobs
        )
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    jobs = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    total_jobs = len(jobs)
    total_apps = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    conn.close()
    return render_template("index.html", jobs=jobs, total_jobs=total_jobs, total_apps=total_apps)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password. Use test credentials provided on page.", "danger")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))

@app.route("/job/<int:job_id>")
def job_detail(job_id):
    conn = get_db()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    already_applied = False
    if "user_id" in session:
        app_check = conn.execute(
            "SELECT id FROM applications WHERE user_id = ? AND job_id = ?",
            (session["user_id"], job_id)
        ).fetchone()
        already_applied = app_check is not None
    conn.close()
    if not job:
        flash("Job posting not found.", "warning")
        return redirect(url_for("index"))
    return render_template("job_detail.html", job=job, already_applied=already_applied)

@app.route("/apply/<int:job_id>", methods=["POST"])
def apply_job(job_id):
    if "user_id" not in session:
        flash("Please log in as a student to submit an application.", "warning")
        return redirect(url_for("login"))
    
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM applications WHERE user_id = ? AND job_id = ?",
        (session["user_id"], job_id)
    ).fetchone()
    
    if existing:
        flash("You have already applied for this role.", "info")
    else:
        conn.execute("INSERT INTO applications (user_id, job_id) VALUES (?, ?)", (session["user_id"], job_id))
        conn.commit()
        flash("Application submitted successfully!", "success")
    conn.close()
    return redirect(url_for("job_detail", job_id=job_id))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("role") != "admin":
        flash("Administrator access required.", "danger")
        return redirect(url_for("login"))
        
    conn = get_db()
    if request.method == "POST":
        title = request.form.get("title")
        company = request.form.get("company")
        location = request.form.get("location")
        salary = request.form.get("salary")
        description = request.form.get("description")
        
        if title and company and location and salary and description:
            conn.execute(
                "INSERT INTO jobs (title, company, location, salary, description) VALUES (?, ?, ?, ?, ?)",
                (title, company, location, salary, description)
            )
            conn.commit()
            flash("New job opportunity posted successfully!", "success")
            return redirect(url_for("admin"))
        else:
            flash("All fields are required.", "warning")

    applications = conn.execute("""
        SELECT a.id, u.name as student_name, u.email as student_email, 
               j.title as job_title, j.company as company, a.applied_at, a.status
        FROM applications a
        JOIN users u ON a.user_id = u.id
        JOIN jobs j ON a.job_id = j.id
        ORDER BY a.id DESC
    """).fetchall()
    
    jobs = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", applications=applications, jobs=jobs)

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Placement & Internship Portal",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("Placement Portal running on http://127.0.0.1:5000")
    print("Admin:   admin@test.com   / admin123")
    print("Student: student@test.com / student123")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
