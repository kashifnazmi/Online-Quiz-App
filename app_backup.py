from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "kashif_quiz_secret_key"

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option1 TEXT NOT NULL,
        option2 TEXT NOT NULL,
        option3 TEXT NOT NULL,
        option4 TEXT NOT NULL,
        answer TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        score INTEGER NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]

    if count == 0:
        questions = [
            ("HTML stands for?", "Hyper Text Markup Language", "High Text Machine Language", "Hyper Tool Markup Language", "None", "Hyper Text Markup Language"),
            ("CSS is used for?", "Database", "Styling", "Server", "Logic", "Styling"),
            ("Python is a?", "Markup Language", "Programming Language", "Database", "Browser", "Programming Language"),
            ("Flask is a?", "Python Framework", "CSS Library", "Database", "OS", "Python Framework"),
            ("SQLite is a?", "Database", "Programming Language", "Browser", "Editor", "Database")
        ]

        cursor.executemany("""
        INSERT INTO questions(question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?)
        """, questions)

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered!"

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = user[1]
            return redirect('/dashboard')
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template("dashboard.html", username=session['user'])

@app.route('/quiz')
def quiz():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    conn.close()

    return render_template("quiz.html", questions=questions)
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    score = 0

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, answer FROM questions")
    answers = cursor.fetchall()

    for q in answers:
        question_id = str(q[0])
        correct_answer = q[1]
        user_answer = request.form.get(question_id)

        if user_answer == correct_answer:
            score += 1

    total = len(answers)
    accuracy = round((score / total) * 100)

    if accuracy >= 80:
        performance = "Excellent"
        stars = "⭐⭐⭐⭐⭐"
    elif accuracy >= 60:
        performance = "Good"
        stars = "⭐⭐⭐⭐"
    elif accuracy >= 40:
        performance = "Average"
        stars = "⭐⭐⭐"
    else:
        performance = "Needs Improvement"
        stars = "⭐⭐"

    cursor.execute(
        "INSERT INTO leaderboard(username, score) VALUES (?, ?)",
        (username, score)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        username=username,
        score=score,
        total=total,
        accuracy=accuracy,
        performance=performance,
        stars=stars
    )