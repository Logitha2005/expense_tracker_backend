from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# ✅ Enable full CORS (important for Flutter web & mobile)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({"message": "Expense Tracker API is running successfully!"})

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # For testing purpose only
        return jsonify({"status": "success", "message": f"User {name} registered successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # ✅ Dummy credentials
        if email == "testuser@example.com" and password == "Test@1234":
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user_id": 1
            })
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
