import fitz
from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
from flask_cors import CORS
from gemini import upload_pdf_and_create_db, answer_question
import os
from google.cloud import vision
import traceback
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/credentials/iprc-456620-6454ff816526.json"

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'deepakbhagat'

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

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

vision_client = vision.ImageAnnotatorClient()

@app.route('/upload', methods=['POST'])
def upload_pdf_or_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        ext = file.filename.lower().split('.')[-1]

        if ext in ['pdf']:
            extracted_text = extract_text_from_pdf(filepath)

        elif ext in ['jpg', 'jpeg', 'png']:
            # ✅ Extract text from image using Vision API
            with open(filepath, "rb") as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            response = vision_client.text_detection(image=image)
            texts = response.text_annotations

            if response.error.message:
                raise Exception(response.error.message)

            if texts:
                extracted_text = texts[0].description
            else:
                extracted_text = ""
                return jsonify({"error": "No text found in image"}), 400

        else:
            return jsonify({"error": "Unsupported file type"}), 400

        msg, success = upload_pdf_and_create_db(extracted_text)
        print(msg)

        if not success:
            print("File failed to process, please try again.")

        return jsonify({"message": msg, "success": success}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

import pdfplumber

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text



@app.route('/', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')

    response = answer_question(question)
    print(f"Response before split: {response}")

    lines = response.strip().split("\n")

    response_text = ""
    confidence_score = "Confidence: 0"

    for line in lines:
        if line.startswith("Response:"):
            response_text = line.replace("Response:", "").strip()
        elif line.startswith("Confidence:"):
            confidence_score = line.strip()
    
    print(f"Response after split: {response_text}")
    print(f"Confidence score: {confidence_score}")

    try:
        confidence = int(confidence_score.replace("Confidence:", "").replace("%", "").strip())
    except ValueError:
        print(f"Error converting confidence: {confidence_score}")
        confidence = 0

    return jsonify({'answer': response_text, 'confidence': confidence})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

