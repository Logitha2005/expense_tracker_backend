from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ---------- Database Setup ----------
def get_db_connection():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return jsonify({"message": "Expense Tracker Backend running successfully!"})


# ---------- Dummy Login Route ----------
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form  # Flutter sends as form-data
        email = data.get('email')
        password = data.get('password')

        # Dummy check (you can replace this with DB later)
        if email == "test@gmail.com" and password == "1234":
            return jsonify({"status": "success", "message": "Login successful!"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------- Add Expense ----------
@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    try:
        data = request.get_json()
        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description', '')

        if not amount or not category:
            return jsonify({'status': 'error', 'message': 'Amount and category are required'}), 400

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)',
            (amount, category, description)
        )
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Expense added successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# ---------- Get All Expenses ----------
@app.route('/api/get_expenses', methods=['GET'])
def get_expenses():
    try:
        conn = get_db_connection()
        expenses = conn.execute('SELECT * FROM expenses').fetchall()
        conn.close()

        expense_list = []
        for exp in expenses:
            expense_list.append({
                'id': exp['id'],
                'amount': exp['amount'],
                'category': exp['category'],
                'description': exp['description']
            })

        return jsonify({'status': 'success', 'data': expense_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# ---------- Create Table (Run Once) ----------
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()


create_table()

# ---------- Run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
