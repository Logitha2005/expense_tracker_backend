from flask import Flask, jsonify, request, send_file, make_response
from flask_cors import CORS
import sqlite3
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DB_FILE = os.path.join(os.path.dirname(__file__), "expenses.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return jsonify({"message": "Expense Tracker Backend running successfully!"})

# ---------- User: register ----------
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.form or request.get_json() or {}
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'status':'error','message':'Email and password required'}), 400

        conn = get_db_connection()
        # check if exists
        existing = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'status':'error','message':'Email already registered'}), 409

        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, password))
        conn.commit()
        user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        return jsonify({'status':'success','message':'Registered','user_id': user['id']}), 200
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- User: login ----------
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form or request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'status':'error','message':'Email and password required'}), 400

        conn = get_db_connection()
        user = conn.execute('SELECT id, name, email FROM users WHERE email = ? AND password = ?',
                            (email, password)).fetchone()
        conn.close()
        if user:
            return jsonify({'status':'success','message':'Login successful','user_id': user['id'], 'name': user['name'], 'email': user['email']}), 200
        else:
            return jsonify({'status':'error','message':'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- Add Expense (JSON) ----------
@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    try:
        data = request.get_json(force=True)
        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description', '')
        user_id = data.get('user_id')  # required
        date_str = data.get('date')  # optional ISO string, e.g. '2025-10-31'

        if not amount or not category or not user_id:
            return jsonify({'status':'error','message':'amount, category and user_id required'}), 400

        # normalize date
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
            except:
                dt = datetime.utcnow()
        else:
            dt = datetime.utcnow()
        date_iso = dt.isoformat()

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)',
            (user_id, amount, category, description, date_iso)
        )
        conn.commit()
        conn.close()
        return jsonify({'status':'success','message':'Expense added successfully!'}), 200
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- Edit Expense ----------
@app.route('/api/edit_expense/<int:expense_id>', methods=['PUT'])
def edit_expense(expense_id):
    try:
        data = request.get_json(force=True)
        amount = data.get('amount')
        category = data.get('category')
        description = data.get('description', '')
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'status':'error','message':'user_id required'}), 400

        conn = get_db_connection()
        # ensure expense belongs to user
        row = conn.execute('SELECT * FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id)).fetchone()
        if not row:
            conn.close()
            return jsonify({'status':'error','message':'Expense not found or not yours'}), 404

        conn.execute('UPDATE expenses SET amount=?, category=?, description=? WHERE id=?',
                     (amount or row['amount'], category or row['category'], description, expense_id))
        conn.commit()
        conn.close()
        return jsonify({'status':'success','message':'Expense updated'}), 200
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- Delete Expense ----------
@app.route('/api/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        user_id = request.args.get('user_id') or (request.get_json() or {}).get('user_id')
        if not user_id:
            return jsonify({'status':'error','message':'user_id required'}), 400
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id)).fetchone()
        if not row:
            conn.close()
            return jsonify({'status':'error','message':'Expense not found or not yours'}), 404
        conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()
        return jsonify({'status':'success','message':'Expense deleted'}), 200
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- Get Expenses (with filters) ----------
@app.route('/api/get_expenses', methods=['GET'])
def get_expenses():
    try:
        user_id = request.args.get('user_id')
        category = request.args.get('category')
        date_from = request.args.get('date_from')  # ISO format
        date_to = request.args.get('date_to')

        if not user_id:
            return jsonify({'status':'error','message':'user_id required'}), 400

        sql = 'SELECT * FROM expenses WHERE user_id = ?'
        params = [user_id]

        if category:
            sql += ' AND category = ?'
            params.append(category)
        if date_from:
            sql += ' AND date >= ?'
            params.append(date_from)
        if date_to:
            sql += ' AND date <= ?'
            params.append(date_to)

        sql += ' ORDER BY date DESC'

        conn = get_db_connection()
        rows = conn.execute(sql, params).fetchall()
        conn.close()

        expense_list = []
        for r in rows:
            expense_list.append({
                'id': r['id'],
                'amount': r['amount'],
                'category': r['category'],
                'description': r['description'],
                'date': r['date']
            })
        return jsonify({'status':'success','data':expense_list}), 200
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- Summary / Totals ----------
@app.route('/api/summary', methods=['GET'])
def summary():
    try:
        user_id = request.args.get('user_id')
        period = request.args.get('period')  # 'day','month','year','all'
        if not user_id:
            return jsonify({'status':'error','message':'user_id required'}), 400

        conn = get_db_connection()
        if period == 'day':
            q = "SELECT date(date) as thedate, SUM(amount) as total FROM expenses WHERE user_id=? GROUP BY date(date)"
            rows = conn.execute(q, (user_id,)).fetchall()
            data = [{r['thedate']: r['total']} for r in rows]
        elif period == 'month':
            q = "SELECT strftime('%Y-%m', date) as mo, SUM(amount) as total FROM expenses WHERE user_id=? GROUP BY mo"
            rows = conn.execute(q, (user_id,)).fetchall()
            data = [{r['mo']: r['total']} for r in rows]
        elif period == 'year':
            q = "SELECT strftime('%Y', date) as yr, SUM(amount) as total FROM expenses WHERE user_id=? GROUP BY yr"
            rows = conn.execute(q, (user_id,)).fetchall()
            data = [{r['yr']: r['total']} for r in rows]
        else:
            q = "SELECT SUM(amount) as total FROM expenses WHERE user_id=?"
            rows = conn.execute(q, (user_id,)).fetchall()
            data = rows[0]['total'] if rows else 0
        conn.close()
        return jsonify({'status':'success','data':data}), 200
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- Export CSV ----------
@app.route('/api/export', methods=['GET'])
def export_csv():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'status':'error','message':'user_id required'}), 400
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC', (user_id,)).fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id','amount','category','description','date'])
        for r in rows:
            writer.writerow([r['id'], r['amount'], r['category'], r['description'], r['date']])

        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        output.close()

        response = make_response(mem.read())
        response.headers.set('Content-Disposition', 'attachment', filename='expenses.csv')
        response.headers.set('Content-Type', 'text/csv')
        return response
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# ---------- Create Tables (run once) ----------
def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
