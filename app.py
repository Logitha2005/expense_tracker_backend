from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ Your MySQL Database Config
app.config['MYSQL_HOST'] = 'your_mysql_host'
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'your_database_name'

mysql = MySQL(app)

# ✅ Health check route
@app.route('/')
def home():
    return jsonify({"message": "Backend is running successfully!"})


# ✅ Route to Add Expense
@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    category = data.get('category')
    description = data.get('description')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO expenses (user_id, amount, category, description)
            VALUES (%s, %s, %s, %s)
        """, (user_id, amount, category, description))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"status": "success", "message": "Expense added successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ✅ Route to Get Expenses
@app.route('/api/get_expenses', methods=['GET'])
def get_expenses():
    user_id = request.args.get('user_id')

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id, amount, category, description
            FROM expenses
            WHERE user_id = %s
            ORDER BY id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        cursor.close()

        # Convert to readable list
        expenses = []
        for row in rows:
            expenses.append({
                "id": row[0],
                "amount": row[1],
                "category": row[2],
                "description": row[3]
            })

        return jsonify({"status": "success", "data": expenses})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ✅ Run app (for local testing)
if __name__ == '__main__':
    app.run(debug=True)
