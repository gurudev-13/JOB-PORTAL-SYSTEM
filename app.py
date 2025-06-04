from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'job_portal.db'

def init_db():
    # Check if database file exists
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Create jobs table
        cursor.execute('''
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                salary TEXT,
                status TEXT NOT NULL,
                posted_at DATETIME NOT NULL
            )
        ''')
        
        # Create applications table
        cursor.execute('''
            CREATE TABLE applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                candidate_name TEXT NOT NULL,
                candidate_email TEXT NOT NULL,
                resume TEXT NOT NULL,
                cover_letter TEXT,
                status TEXT NOT NULL,
                applied_at DATETIME NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database and tables created successfully.")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM jobs WHERE status = "open"').fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs)

@app.route('/search', methods=['GET'])
def search_jobs():
    query = request.args.get('query', '')
    conn = get_db_connection()
    jobs = conn.execute(
        'SELECT * FROM jobs WHERE status = "open" AND (title LIKE ? OR description LIKE ?)',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs, query=query)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    if job:
        return render_template('job_detail.html', job=job)
    else:
        flash('Job not found.')
        return redirect(url_for('index'))

@app.route('/apply/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    resume = request.form['resume']
    cover_letter = request.form['cover_letter']
    candidate_name = request.form['candidate_name']
    candidate_email = request.form['candidate_email']
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO applications (job_id, candidate_name, candidate_email, resume, cover_letter, status, applied_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (job_id, candidate_name, candidate_email, resume, cover_letter, 'pending', datetime.now())
    )
    conn.commit()
    conn.close()
    flash('Application submitted successfully!')
    return redirect(url_for('index'))

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        company = request.form['company']
        location = request.form['location']
        salary = request.form['salary']
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO jobs (title, description, company, location, salary, status, posted_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, description, company, location, salary, 'open', datetime.now())
        )
        conn.commit()
        conn.close()
        flash('Job posted successfully!')
        return redirect(url_for('index'))
    return render_template('post_job.html')

@app.route('/manage_jobs')
def manage_jobs():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM jobs').fetchall()
    conn.close()
    return render_template('manage_jobs.html', jobs=jobs)

@app.route('/job/<int:job_id>/applications')
def view_applications(job_id):
    conn = get_db_connection()
    applications = conn.execute('SELECT * FROM applications WHERE job_id = ?', (job_id,)).fetchall()
    conn.close()
    return jsonify([dict(app) for app in applications])

@app.route('/application/<int:app_id>/update', methods=['POST'])
def update_application(app_id):
    status = request.form['status']
    conn = get_db_connection()
    conn.execute('UPDATE applications SET status = ? WHERE id = ?', (status, app_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Application status updated'})

if __name__ == '__main__':
    init_db()  # Initialize database before running the app
    app.run(debug=True)