from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
from flask_cors import CORS  # Allow requests from frontend

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
SECRET_KEY = 'deepakbhagat'

# JWT authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Token should be sent in the Authorization header as Bearer <token>
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            if bearer.startswith("Bearer "):
                token = bearer[7:]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data['email']  # optional: save user info in request context
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

# 👇 Example of protected route
@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': f'Hello {request.user}, you accessed a protected route!'})

# 👇 You can wrap other routes similarly
@app.route('/upload', methods=['POST'])
@token_required
def upload():
    return jsonify({'message': 'PDF uploaded successfully (dummy response)'})

@app.route('/', methods=['POST'])
@token_required
def ask_question():
    question = request.json.get('question', '')
    return jsonify({'answer': f'Dummy answer for: {question}'})

if __name__ == '__main__':
    app.run(debug=True)
