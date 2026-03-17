from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import re
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ─── DB CONFIG ───────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'abc@9862',
    'database': 'student_portal',
    'auth_plugin': 'mysql_native_password'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ─── HOME ────────────────────────────────────
@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ─── LOGIN ───────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s',
                       (username, hash_password(password)))
        account = cursor.fetchone()
        db.close()
        if account:
            session['loggedin'] = True
            session['id']       = account['id']
            session['username'] = account['username']
            session['role']     = account['role']
            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username or password.'
    return render_template('login.html', msg=msg)


# ─── SIGNUP ──────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    msg = ''
    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        password  = request.form.get('password', '')
        email     = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Username already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out all required fields!'
        elif len(password) < 6:
            msg = 'Password must be at least 6 characters!'
        else:
            cursor.execute(
                'INSERT INTO users (username, password, email, full_name, role) VALUES (%s,%s,%s,%s,%s)',
                (username, hash_password(password), email, full_name, 'student')
            )
            db.commit()
            db.close()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        db.close()
    return render_template('signup.html', msg=msg)


# ─── LOGOUT ──────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─── DASHBOARD ───────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id=%s', (session['id'],))
    account = cursor.fetchone()
    cursor.execute('SELECT * FROM grades WHERE user_id=%s', (session['id'],))
    grades = cursor.fetchall()
    cursor.execute(
        'SELECT d.*, u.username as shared_by FROM documents d '
        'JOIN users u ON d.uploaded_by=u.id '
        'WHERE d.is_public=1 OR d.uploaded_by=%s ORDER BY d.created_at DESC',
        (session['id'],)
    )
    documents = cursor.fetchall()
    db.close()
    return render_template('dashboard.html', account=account, grades=grades, documents=documents)


# ─── PROFILE ─────────────────────────────────
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    msg = ''
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip()
        phone     = request.form.get('phone', '').strip()
        bio       = request.form.get('bio', '').strip()
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        else:
            cursor.execute(
                'UPDATE users SET full_name=%s, email=%s, phone=%s, bio=%s WHERE id=%s',
                (full_name, email, phone, bio, session['id'])
            )
            db.commit()
            db.close()
            flash('Profile updated!', 'success')
            return redirect(url_for('profile'))
    cursor.execute('SELECT * FROM users WHERE id=%s', (session['id'],))
    account = cursor.fetchone()
    db.close()
    return render_template('profile.html', account=account, msg=msg)


# ─── RESET PASSWORD ──────────────────────────
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    msg = ''
    if request.method == 'POST':
        current  = request.form.get('current_password', '')
        new_pw   = request.form.get('new_password', '')
        confirm  = request.form.get('confirm_password', '')
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id=%s AND password=%s',
                       (session['id'], hash_password(current)))
        account = cursor.fetchone()
        if not account:
            msg = 'Current password is incorrect!'
        elif new_pw != confirm:
            msg = 'New passwords do not match!'
        elif len(new_pw) < 6:
            msg = 'Password must be at least 6 characters!'
        else:
            cursor.execute('UPDATE users SET password=%s WHERE id=%s',
                           (hash_password(new_pw), session['id']))
            db.commit()
            db.close()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('profile'))
        db.close()
    return render_template('reset_password.html', msg=msg)


# ─── GRADES ──────────────────────────────────
@app.route('/grades')
def grades():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM grades WHERE user_id=%s ORDER BY subject', (session['id'],))
    grades = cursor.fetchall()
    db.close()
    grade_points = {'A+':10,'A':9,'B+':8,'B':7,'C+':6,'C':5,'D':4,'F':0}
    total_gp = sum(grade_points.get(g['grade'], 0) for g in grades)
    gpa = round(total_gp / len(grades), 2) if grades else 0
    return render_template('grades.html', grades=grades, gpa=gpa)


# ─── ADMIN GRADES ────────────────────────────
@app.route('/admin/grades', methods=['GET', 'POST'])
def admin_grades():
    if 'loggedin' not in session or session.get('role') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            cursor.execute(
                'INSERT INTO grades (user_id, subject, marks, grade) VALUES (%s,%s,%s,%s)',
                (request.form['user_id'], request.form['subject'],
                 request.form['marks'], request.form['grade'])
            )
        elif action == 'update':
            cursor.execute(
                'UPDATE grades SET marks=%s, grade=%s WHERE id=%s',
                (request.form['marks'], request.form['grade'], request.form['grade_id'])
            )
        elif action == 'delete':
            cursor.execute('DELETE FROM grades WHERE id=%s', (request.form['grade_id'],))
        db.commit()
        flash('Grade updated!', 'success')
    cursor.execute(
        'SELECT g.*, u.username FROM grades g JOIN users u ON g.user_id=u.id ORDER BY u.username'
    )
    all_grades = cursor.fetchall()
    cursor.execute('SELECT id, username, full_name FROM users WHERE role="student" ORDER BY username')
    students = cursor.fetchall()
    db.close()
    return render_template('admin_grades.html', all_grades=all_grades, students=students)


# ─── DOCUMENTS ───────────────────────────────
@app.route('/documents', methods=['GET', 'POST'])
def documents():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        content     = request.form.get('content', '').strip()
        is_public   = 1 if request.form.get('is_public') else 0
        if title and content:
            cursor.execute(
                'INSERT INTO documents (title, description, content, uploaded_by, is_public) VALUES (%s,%s,%s,%s,%s)',
                (title, description, content, session['id'], is_public)
            )
            db.commit()
            flash('Document shared!', 'success')
        else:
            flash('Title and content required!', 'danger')
    cursor.execute(
        'SELECT d.*, u.username as shared_by FROM documents d '
        'JOIN users u ON d.uploaded_by=u.id '
        'WHERE d.is_public=1 OR d.uploaded_by=%s ORDER BY d.created_at DESC',
        (session['id'],)
    )
    docs = cursor.fetchall()
    db.close()
    return render_template('documents.html', documents=docs)


# ─── DELETE DOCUMENT ─────────────────────────
@app.route('/documents/delete/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM documents WHERE id=%s', (doc_id,))
    doc = cursor.fetchone()
    if doc and (doc['uploaded_by'] == session['id'] or session.get('role') == 'admin'):
        cursor.execute('DELETE FROM documents WHERE id=%s', (doc_id,))
        db.commit()
        flash('Document deleted.', 'info')
    else:
        flash('Permission denied.', 'danger')
    db.close()
    return redirect(url_for('documents'))


if __name__ == '__main__':
    app.run(debug=True)