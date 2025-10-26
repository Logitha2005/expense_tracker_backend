from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Temporary in-memory storage for expenses
expenses = []

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if email == "abc@gmail.com" and password == "12345":
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/submit', methods=['POST'])
def submit_expense():
    data = request.get_json()
    category = data.get('category')
    description = data.get('description')
    amount = data.get('amount')

    if not category or not description or not amount:
        return jsonify({"message": "Missing fields"}), 400

    # Save expense in memory
    expenses.append({
        "category": category,
        "description": description,
        "amount": amount
    })

    print(f"Received Expense: {category}, {description}, {amount}")
    return jsonify({"message": "Expense added successfully!"}), 200

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(expenses), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
