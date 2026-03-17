-- ============================================================
--  Student Portal Database Schema
--  Run this in MySQL Workbench to set up the database
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_portal;
USE student_portal;

-- ─────────────────────────────────────────────
--  USERS TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,             -- SHA-256 hash
    email      VARCHAR(100) NOT NULL,
    full_name  VARCHAR(100) DEFAULT '',
    phone      VARCHAR(20)  DEFAULT '',
    bio        TEXT         DEFAULT '',
    role       ENUM('student','admin') DEFAULT 'student',
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
--  GRADES TABLE  (students cannot edit)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS grades (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    subject    VARCHAR(100) NOT NULL,
    marks      DECIMAL(5,2) DEFAULT 0,
    grade      VARCHAR(5)   DEFAULT 'N/A',
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  DOCUMENTS TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT         DEFAULT '',
    content     LONGTEXT     NOT NULL,
    uploaded_by INT NOT NULL,
    is_public   TINYINT(1)   DEFAULT 1,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  SEED DATA – default admin account
--  Password: admin123  (SHA-256 hashed)
-- ─────────────────────────────────────────────
INSERT INTO users (username, password, email, full_name, role)
VALUES (
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'admin@studentportal.edu',
    'System Administrator',
    'admin'
);

-- Sample student
INSERT INTO users (username, password, email, full_name, role)
VALUES (
    'student1',
    '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',  -- 123456
    'student1@college.edu',
    'Alice Johnson',
    'student'
);

-- Sample grades for student1
INSERT INTO grades (user_id, subject, marks, grade) VALUES
    (2, 'Mathematics',         87.5, 'A'),
    (2, 'Physics',             76.0, 'B+'),
    (2, 'Computer Science',    95.0, 'A+'),
    (2, 'English',             72.0, 'B'),
    (2, 'Database Management', 88.0, 'A');

-- Sample public document
INSERT INTO documents (title, description, content, uploaded_by, is_public) VALUES
(
    'Welcome to Student Portal',
    'Getting started guide for new students',
    'Welcome to the Student Portal!\n\nThis platform allows you to:\n- View your grades\n- Share documents with classmates\n- Update your personal profile\n- Reset your password securely\n\nFor any issues, contact the administrator.',
    1,
    1
);
