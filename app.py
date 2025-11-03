from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    # You can add logic to save user here
    return jsonify({"status": "success", "message": "User registered successfully!"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Dummy login verification for testing
    if email == "testuser@example.com" and password == "Test@1234":
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user_id": 1
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401

@app.route('/')
def home():
    return jsonify({"message": "Expense Tracker API running!"})

if __name__ == '__main__':
    app.run(debug=True)
