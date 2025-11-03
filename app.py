from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow frontend to call backend

# ✅ MySQL configuration
app.config['MYSQL_HOST'] = 'sql12.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql12753841'
app.config['MYSQL_PASSWORD'] = 'xqkJZ6Zq7S'
app.config['MYSQL_DB'] = 'sql12753841'

mysql = MySQL(app)

# ✅ SIGNUP endpoint
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        return jsonify({'status': 'error', 'message': 'User already exists'}), 400

    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                   (name, email, password))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'status': 'success', 'message': 'Signup successful!'}), 200


# ✅ LOGIN endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify({'status': 'success', 'user_id': user[0]})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401


# ✅ FETCH EXPENSES
@app.route('/api/get_expenses', methods=['GET'])
def get_expenses():
    user_id = request.args.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, title, amount, category, date FROM expenses WHERE user_id=%s", (user_id,))
    expenses = cursor.fetchall()
    cursor.close()

    result = [
        {
            'id': row[0],
            'title': row[1],
            'amount': row[2],
            'category': row[3],
            'date': row[4]
        }
        for row in expenses
    ]

    return jsonify({'status': 'success', 'expenses': result})


# ✅ ADD EXPENSE
@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    amount = data.get('amount')
    category = data.get('category')

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO expenses (user_id, title, amount, category) VALUES (%s, %s, %s, %s)",
                   (user_id, title, amount, category))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'status': 'success', 'message': 'Expense added!'})


@app.route('/')
def home():
    return "Expense Tracker Backend is running!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
