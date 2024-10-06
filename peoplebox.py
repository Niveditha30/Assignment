from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('job_recommendation.db')
    conn.row_factory = sqlite3.Row
    return conn

# Database setup (run once to create tables)
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # User Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills TEXT,
            experience INTEGER,
            preferences TEXT
        )
    ''')

    # Job Postings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            required_skills TEXT,
            experience_required INTEGER,
            location TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Insert example data (run once)
def insert_sample_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sample user profile
    cursor.execute('''
        INSERT INTO user_profiles (name, skills, experience, preferences)
        VALUES ('Alice', 'Python, Flask, SQL', 3, 'remote')
    ''')

    # Sample job postings
    cursor.execute('''
        INSERT INTO job_postings (title, required_skills, experience_required, location)
        VALUES ('Backend Developer', 'Python, Flask', 2, 'remote'),
               ('Data Analyst', 'SQL, Python', 1, 'onsite'),
               ('Frontend Developer', 'React, CSS', 2, 'remote')
    ''')

    conn.commit()
    conn.close()

# Recommendation Logic
def recommend_jobs(user_profile):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Split the user's skills and preferences for matching
    user_skills = user_profile['skills'].split(', ')
    user_experience = user_profile['experience']
    user_preferences = user_profile['preferences']

    # Query jobs matching user skills and experience
    cursor.execute('''
        SELECT * FROM job_postings WHERE
        (experience_required <= ?) AND
        (location = ? OR location = 'remote')
    ''', (user_experience, user_preferences))

    jobs = cursor.fetchall()
    conn.close()

    # Simple skill matching (rule-based, extend as needed)
    recommended_jobs = []
    for job in jobs:
        job_skills = job['required_skills'].split(', ')
        if any(skill in user_skills for skill in job_skills):
            recommended_jobs.append(dict(job))

    return recommended_jobs

# API: Recommend Jobs based on user profile
@app.route('/recommend_jobs', methods=['POST'])
def recommend_jobs_endpoint():
    user_profile = request.json
    if not user_profile:
        return jsonify({'error': 'No user profile provided'}), 400
    
    try:
        recommended_jobs = recommend_jobs(user_profile)
        return jsonify(recommended_jobs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Uncomment the following lines to create tables and insert sample data initially
    # create_tables()
    # insert_sample_data()
    
    app.run(debug=True)
