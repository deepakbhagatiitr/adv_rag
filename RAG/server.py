# main Flask app file
from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
from flask_cors import CORS
from gemini import upload_pdf_and_create_db, answer_question
import os

import traceback


app = Flask(__name__)
CORS(app)
SECRET_KEY = 'deepakbhagat'

# ---------------- JWT Logic ----------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            if bearer.startswith("Bearer "):
                token = bearer[7:]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# ---------------- Routes ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data['email'] == 'user@example.com' and data['password'] == 'deepak':
        token = jwt.encode({
            'email': data['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': f'Hello {request.user}, you accessed a protected route!'})



UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

import fitz

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # ✅ Extract text from PDF
        pdf_text = extract_text_from_pdf(filepath)

        # ✅ Pass extracted text to gemini logic
        msg, success = upload_pdf_and_create_db(pdf_text)
        print(msg)

        if not success:
            # Optional: Add retry or error dialog on frontend
            print("PDF failed to process, please try again.")


        return jsonify({"message": success}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ✅ PDF Text Extraction Function
import pdfplumber

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text

# text = extract_text_from_pdf('path_to_pdf.pdf')
# print(text)



@app.route('/', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')
    answer = answer_question(question)
    return jsonify({'answer': answer})


if __name__ == '__main__':
    app.run(debug=True)
