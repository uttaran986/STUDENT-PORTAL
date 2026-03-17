# Student Portal

A web application for user authentication and document sharing, built with Flask and MySQL.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.4-orange?style=flat-square&logo=mysql)

---

## Screenshots

### Login
![Login](screenshots/login.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

---

## Built With

- **Flask** — Python web framework
- **MySQL** — Database
- **mysql-connector-python** — Database connector
- **HTML5 / CSS3 / JavaScript** — Frontend
- **SHA-256** — Password hashing
- **Visual Studio Code** — IDE

---

## Features

- User registration and login
- Profile editing and password reset
- Grade viewing (read-only)
- Document sharing
- Admin panel for managing grades
- Role-based access (Student / Admin)
- Dark themed responsive UI

---

## How to Run

```bash
# 1. Clone the repo
git clone https://github.com/uttaranpal/student-portal.git
cd student-portal

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install Flask mysql-connector-python

# 4. Run schema.sql in MySQL Workbench

# 5. Update DB password in app.py

# 6. Start the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## Author

**Uttaran Pal**
