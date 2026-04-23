from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from face_utils import process_face_image, compare_faces
from database import connect_to_dynamodb, save_user, get_user_by_email, create_users_table
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_paris_2026"

db = connect_to_dynamodb()
if db:
    create_users_table(db)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        face_data = request.form.get('face_image')

        encoding = process_face_image(face_data)
        if not encoding: return "Visage non détecté", 400

        user_item = {
            'email': email,
            'password': generate_password_hash(password),
            'face_encoding': encoding,
            'created_at': datetime.now().isoformat()
        }
        if save_user(db, user_item):
            return redirect(url_for('login'))
        return "Erreur base de données", 500
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = get_user_by_email(db, email)
        if user and check_password_hash(user['password'], password):
            session['user'] = email
            return redirect(url_for('index'))
        return "Identifiants invalides", 401
    return render_template('login.html')

@app.route('/login/face', methods=['POST'])
def login_face():
    data = request.json
    user = get_user_by_email(db, data.get('email'))
    if user and compare_faces(user['face_encoding'], data.get('image')):
        session['user'] = user['email']
        return jsonify({"status": "success"})
    return jsonify({"status": "fail", "message": "Échec reconnaissance"}), 401

@app.route('/index')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)