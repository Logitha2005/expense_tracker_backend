from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Temporary in-memory database
expenses = []
next_id = 1

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

        return jsonify({"status": "success", "message": f"User {name} registered successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

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


# 🟢 ADD EXPENSE
@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    global next_id
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        category = data.get('category')
        amount = data.get('amount')
        date = data.get('date')

        if not (user_id and category and amount and date):
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        new_expense = {
            "id": next_id,
            "user_id": user_id,
            "category": category,
            "amount": amount,
            "date": date
        }
        expenses.append(new_expense)
        next_id += 1

        return jsonify({"status": "success", "message": "Expense added successfully!", "expense": new_expense})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 🟢 GET EXPENSES
@app.route('/api/expenses/<int:user_id>', methods=['GET'])
def get_expenses(user_id):
    user_expenses = [e for e in expenses if e["user_id"] == user_id]
    return jsonify({"status": "success", "expenses": user_expenses})


# 🟢 DELETE EXPENSE
@app.route('/api/expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    global expenses
    expenses = [e for e in expenses if e["id"] != expense_id]
    return jsonify({"status": "success", "message": "Expense deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True)
