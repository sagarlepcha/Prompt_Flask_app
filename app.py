from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Prompt
from collections import defaultdict
import sqlite3
from rapidfuzz import fuzz

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prompts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db.init_app(app)

def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            is_admin INTEGER DEFAULT 0
                        )''')
        conn.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('secret', 'secret', 1)")
init_db()

def get_best_matches(query, prompts, threshold=50):
    matches = []
    for p in prompts:
        score = fuzz.partial_ratio(query, p)
        if score >= threshold:
            matches.append((p, score))
    return [match[0] for match in sorted(matches, key=lambda x: -x[1])]

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return redirect(url_for('index'))

    all_prompts = Prompt.query.all()
    prompt_texts = [prompt.text for prompt in all_prompts]

    # Use fuzzy matching
    close_matches = get_best_matches(query, prompt_texts, threshold=50)

    categorized = defaultdict(list)
    for prompt in all_prompts:
        if prompt.text in close_matches:
            categorized[prompt.category].append(prompt.text)

    return render_template('index.html', prompts=categorized, is_logged_in='username' in session, query=query)




@app.route('/')
def index():
    all_prompts = Prompt.query.all()
    categorized_prompts = defaultdict(list)
    for prompt in all_prompts:
        categorized_prompts[prompt.category].append(prompt.text)
    is_logged_in = 'username' in session
    return render_template('index.html', prompts=categorized_prompts,is_logged_in=is_logged_in)




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                flash('Signup successful. Please login.')
                return redirect(url_for('login'))
            except:
                flash('Username already exists.')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
            if user:
                session['username'] = user[1]
                session['is_admin'] = user[3]
                if user[3] == 1:
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('index'))
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session.get('is_admin') != 1:
        
        return redirect(url_for('login'))
    prompts = Prompt.query.all()
    return render_template('admin_dashboard.html', username=session['username'], prompts=prompts)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_prompt():
    if 'username' not in session or session.get('is_admin') != 1:
        
        return redirect(url_for('login'))
    if request.method == 'POST':
        prompt_text = request.form['prompt']
        category = request.form['category']
        if prompt_text and category:
            new_prompt = Prompt(text=prompt_text, category=category)
            db.session.add(new_prompt)
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_add.html') 


@app.route('/admin/delete/<int:id>', methods=['GET'])
def delete_prompt(id):
    if 'username' not in session or session.get('is_admin') != 1:
        
        return redirect(url_for('login'))
    prompt = Prompt.query.get_or_404(id)
    db.session.delete(prompt)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update/<int:id>', methods=['GET', 'POST'])
def update_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    if 'username' not in session or session.get('is_admin') != 1:
        
        return redirect(url_for('login'))
    if request.method == 'POST':
        prompt.text = request.form['prompt']
        prompt.category = request.form['category']  # Update category
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('update.html', prompt=prompt)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
