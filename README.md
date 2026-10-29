# Student Placement & Internship Portal (Demo)

A complete, self-contained Python Flask web application for testing and demonstration.
Uses built-in SQLite (zero external database configuration required).

## Features
- **Job Board:** View active campus placement and internship postings.
- **Authentication:** Role-based login (Student & Administrator).
- **Application Flow:** Students can view roles and submit applications with 1 click.
- **Admin Dashboard:** Placement officers can post new openings and review candidate applications.
- **REST API:** `/api/health` endpoint for automated ping/health verification.

---

## Quick Setup & Run Instructions

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Web Portal
Open your browser and navigate to:
**http://127.0.0.1:5000**

---

## Pre-configured Demo Accounts

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Placement Admin** | `admin@test.com` | `admin123` | Post new jobs, view all student applications |
| **Student** | `student@test.com` | `student123` | Browse job listings, apply for jobs |

---

## Verification
- API Health Check: `http://127.0.0.1:5000/api/health` returns `{"status": "healthy"}`.
