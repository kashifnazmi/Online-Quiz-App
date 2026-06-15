from flask import Flask, render_template, request, redirect, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
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
        category TEXT NOT NULL,
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
        category TEXT NOT NULL,
        score INTEGER NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]

    if count == 0:
        questions = [
            ("HTML","HTML stands for?","Hyper Text Markup Language","High Text Machine Language","Hyper Tool Markup Language","None","Hyper Text Markup Language"),
            ("HTML","Which tag creates a hyperlink?","a","link","href","url","a"),
            ("HTML","Which tag is used for image?","img","image","src","picture","img"),
            ("HTML","Which tag is used for paragraph?","p","para","text","h1","p"),
            ("HTML","Which tag is used for table?","table","tr","td","tb","table"),
            ("HTML","Which tag is used for line break?","br","break","lb","hr","br"),
            ("HTML","Which tag is used for form?","form","input","label","fieldset","form"),
            ("HTML","Which attribute specifies URL?","href","src","url","link","href"),
            ("HTML","Which tag is largest heading?","h1","h6","head","title","h1"),
            ("HTML","HTML file extension?",".html",".htm",".web",".page",".html"),

            ("CSS","CSS stands for?","Cascading Style Sheets","Creative Style Sheets","Computer Style Sheets","Color Style Sheets","Cascading Style Sheets"),
            ("CSS","Property to change text color?","color","font","background","style","color"),
            ("CSS","Property for background color?","background-color","color","bg","background","background-color"),
            ("CSS","Property for font size?","font-size","size","font","text-size","font-size"),
            ("CSS","Property for spacing inside element?","padding","margin","gap","border","padding"),
            ("CSS","Property for spacing outside element?","margin","padding","border","gap","margin"),
            ("CSS","Flexbox display value?","flex","block","inline","grid","flex"),
            ("CSS","Property for rounded corners?","border-radius","radius","corner","round","border-radius"),
            ("CSS","Property for shadow?","box-shadow","shadow","text-shadow","glow","box-shadow"),
            ("CSS","Property for text alignment?","text-align","align","justify","font-align","text-align"),

            ("JavaScript","JavaScript is used for?","Interactivity","Database","Server","Styling","Interactivity"),
            ("JavaScript","Keyword to declare variable?","let","echo","varr","define","let"),
            ("JavaScript","Method to print console output?","console.log()","print()","echo()","write()","console.log()"),
            ("JavaScript","Strict equality operator?","===","==","=","!=","==="),
            ("JavaScript","Boolean values?","true/false","yes/no","1/0","on/off","true/false"),
            ("JavaScript","Function to delay execution?","setTimeout","delay","timer","sleep","setTimeout"),
            ("JavaScript","Method to select element by id?","getElementById","queryId","selectId","idSelector","getElementById"),
            ("JavaScript","Array stores?","Multiple values","Single value","Database","Objects only","Multiple values"),
            ("JavaScript","Loop keyword?","for","repeat","loop","iterate","for"),
            ("JavaScript","JS file extension?",".js",".javascript",".jsx",".java",".js"),

            ("Python","Python is a?","Programming Language","Browser","Database","Markup Language","Programming Language"),
            ("Python","Keyword to define function?","def","function","func","define","def"),
            ("Python","Comment symbol?","#","//","<!-- -->","/* */","#"),
            ("Python","Dictionary stores?","Key-value pairs","Numbers","Strings","Lists","Key-value pairs"),
            ("Python","Method to add item in list?","append()","push()","add()","insertEnd()","append()"),
            ("Python","Loop used to iterate?","for","repeat","iterate","loop","for"),
            ("Python","Python file extension?",".py",".python",".pt",".code",".py"),
            ("Python","Framework for web development?","Flask","Bootstrap","React","MySQL","Flask"),
            ("Python","Which datatype stores sequence?","List","Dictionary","Set","Boolean","List"),
            ("Python","Function to display output?","print()","show()","echo()","display()","print()")
        ]

        cursor.executemany("""
        INSERT INTO questions(category, question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, questions)

    conn.commit()
    conn.close()


init_db()


def is_admin():
    return 'user' in session and session['user'] == 'admin'


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

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leaderboard")
    total_attempts = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(score) FROM leaderboard")
    highest_score = cursor.fetchone()[0] or 0

    conn.close()

    categories = ["HTML", "CSS", "JavaScript", "Python"]

    return render_template(
        "dashboard.html",
        username=session['user'],
        categories=categories,
        total_users=total_users,
        total_questions=total_questions,
        total_attempts=total_attempts,
        highest_score=highest_score
    )


@app.route('/quiz/<category>')
def quiz(category):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM questions WHERE category=? ORDER BY RANDOM() LIMIT 5",
        (category,)
    )
    questions = cursor.fetchall()

    conn.close()

    return render_template("quiz.html", questions=questions, category=category)


@app.route('/submit_quiz/<category>', methods=['POST'])
def submit_quiz(category):
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    score = 0

    question_ids = request.form.getlist('question_ids')

    if not question_ids:
        return redirect('/dashboard')

    placeholders = ",".join(["?"] * len(question_ids))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT id, answer FROM questions WHERE id IN ({placeholders})",
        question_ids
    )

    answers = cursor.fetchall()

    for q in answers:
        question_id = str(q[0])
        correct_answer = q[1]
        user_answer = request.form.get(question_id)

        if user_answer == correct_answer:
            score += 1

    total = len(question_ids)
    accuracy = round((score / total) * 100) if total > 0 else 0

    if accuracy >= 80:
        performance = "Excellent"
        stars = "5 Stars"
    elif accuracy >= 60:
        performance = "Good"
        stars = "4 Stars"
    elif accuracy >= 40:
        performance = "Average"
        stars = "3 Stars"
    else:
        performance = "Needs Improvement"
        stars = "2 Stars"

    cursor.execute(
        "INSERT INTO leaderboard(username, category, score) VALUES (?, ?, ?)",
        (username, category, score)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        username=username,
        category=category,
        score=score,
        total=total,
        accuracy=accuracy,
        performance=performance,
        stars=stars
    )


@app.route('/leaderboard')
def leaderboard():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, category, score FROM leaderboard ORDER BY score DESC")
    leaders = cursor.fetchall()

    conn.close()

    return render_template("leaderboard.html", leaders=leaders)


@app.route('/admin')
def admin():
    if not is_admin():
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()

    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT username, category, score FROM leaderboard ORDER BY score DESC")
    scores = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        questions=questions,
        users=users,
        scores=scores
    )


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if not is_admin():
        return redirect('/login')

    if request.method == 'POST':
        category = request.form['category']
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO questions(category, question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category, question, option1, option2, option3, option4, answer))

        conn.commit()
        conn.close()

        return redirect('/admin')

    return render_template("add_question.html")


@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    if not is_admin():
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == 'POST':
        category = request.form['category']
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        cursor.execute("""
        UPDATE questions
        SET category=?, question=?, option1=?, option2=?, option3=?, option4=?, answer=?
        WHERE id=?
        """, (category, question, option1, option2, option3, option4, answer, id))

        conn.commit()
        conn.close()

        return redirect('/admin')

    cursor.execute("SELECT * FROM questions WHERE id=?", (id,))
    question = cursor.fetchone()

    conn.close()

    return render_template("edit_question.html", question=question)


@app.route('/delete_question/<int:id>')
def delete_question(id):
    if not is_admin():
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM questions WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/admin')


@app.route('/certificate/<username>/<category>/<int:score>/<int:total>')
def certificate(username, category, score, total):
    filename = f"{username}_certificate.pdf"

    c = canvas.Canvas(filename)

    c.setFont("Helvetica-Bold", 24)
    c.drawString(150, 750, "Certificate of Achievement")

    c.setFont("Helvetica", 16)
    c.drawString(100, 680, "This certificate is awarded to")

    c.setFont("Helvetica-Bold", 20)
    c.drawString(180, 640, username)

    c.setFont("Helvetica", 16)
    c.drawString(100, 580, f"For successfully completing {category} Quiz")
    c.drawString(100, 540, f"Score: {score}/{total}")
    c.drawString(100, 500, "Online Quiz Application")

    c.save()

    return send_file(filename, as_attachment=True)
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT category, score FROM leaderboard WHERE username=?",
        (username,)
    )
    history = cursor.fetchall()

    total_attempts = len(history)

    if total_attempts > 0:
        scores = [h[1] for h in history]
        highest_score = max(scores)
        average_score = round(sum(scores) / total_attempts, 2)
    else:
        highest_score = 0
        average_score = 0

    badges = []

    if highest_score >= 2:
        badges.append("Perfect Score")

    if total_attempts >= 3:
        badges.append("Active Learner")

    categories_completed = [h[0] for h in history]

    if "HTML" in categories_completed:
        badges.append("HTML Master")

    if "CSS" in categories_completed:
        badges.append("CSS Expert")

    if "JavaScript" in categories_completed:
        badges.append("JavaScript Champion")

    if "Python" in categories_completed:
        badges.append("Python Pro")

    category_stats = {
        "HTML": 0,
        "CSS": 0,
        "JavaScript": 0,
        "Python": 0
    }

    for item in history:
        category = item[0]
        score = item[1]

        if category in category_stats and score > category_stats[category]:
            category_stats[category] = score

    conn.close()

    return render_template(
        "profile.html",
        username=username,
        history=history,
        total_attempts=total_attempts,
        highest_score=highest_score,
        average_score=average_score,
        badges=badges,
        category_stats=category_stats
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)