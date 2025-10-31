from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Enable CORS so Flutter (frontend) can access backend
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Base route
@app.route('/')
def home():
    return jsonify({"message": "Expense Tracker Backend running successfully!"})

# ✅ Test route to check API connectivity
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "data": "API connected properly!"})

# ✅ Example route for login (you can replace with your DB logic)
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    # Dummy logic — replace with database check
    if email == "test@example.com" and password == "1234":
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# ✅ Example route for signup
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    # Dummy success response (replace with DB insert)
    return jsonify({"status": "success", "message": f"User {name} registered successfully!"})

# ✅ Example route to add expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    title = data.get('title')
    amount = data.get('amount')
    category = data.get('category')

    # Dummy success response
    return jsonify({"status": "success", "message": f"Expense '{title}' added!"})

# ✅ Example route to view all expenses
@app.route('/view_expenses', methods=['GET'])
def view_expenses():
    # Dummy expense list
    expenses = [
        {"id": 1, "title": "Groceries", "amount": 500, "category": "Food"},
        {"id": 2, "title": "Electricity Bill", "amount": 1200, "category": "Utilities"},
    ]
    return jsonify({"status": "success", "expenses": expenses})

# ✅ Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

# ✅ Run the app
if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
