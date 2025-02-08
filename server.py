<<<<<<< HEAD
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

DB_FILE = "tasks.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        date TEXT,
                        task_name TEXT,
                        time_spent TEXT)''')
    conn.commit()
    conn.close()

init_db()  # Ensure the database is ready

# Requirement 1: Send the current date to frontend
@app.route('/get-date', methods=['GET'])
def get_date():
    today = datetime.date.today().strftime("%d/%m/%Y")
    return jsonify({"date": today})

# Requirement 2: Save tasks into the database
@app.route('/save-tasks', methods=['POST'])
def save_tasks():
    data = request.json  # Expecting a list of tasks
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for task in data:
        cursor.execute("INSERT INTO tasks (date, task_name, time_spent) VALUES (?, ?, ?)",
                       (task["date"], task["task_name"], task["time_spent"]))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Tasks saved successfully!"})

# Requirement 3: Load previous session tasks (for data persistence)
@app.route('/load-tasks', methods=['GET'])
def load_tasks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today = datetime.date.today().strftime("%d/%m/%Y")

    cursor.execute("SELECT task_name, time_spent FROM tasks WHERE date = ?", (today,))
    tasks = [{"task_name": row[0], "time_spent": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return jsonify({"tasks": tasks})

if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

DB_FILE = "tasks.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        date TEXT,
                        task_name TEXT,
                        time_spent TEXT)''')
    conn.commit()
    conn.close()

init_db()  # Ensure the database is ready

# Requirement 1: Send the current date to frontend
@app.route('/get-date', methods=['GET'])
def get_date():
    today = datetime.date.today().strftime("%d/%m/%Y")
    return jsonify({"date": today})

# Requirement 2: Save tasks into the database
@app.route('/save-tasks', methods=['POST'])
def save_tasks():
    data = request.json  # Expecting a list of tasks
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for task in data:
        cursor.execute("INSERT INTO tasks (date, task_name, time_spent) VALUES (?, ?, ?)",
                       (task["date"], task["task_name"], task["time_spent"]))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Tasks saved successfully!"})

# Requirement 3: Load previous session tasks (for data persistence)
@app.route('/load-tasks', methods=['GET'])
def load_tasks():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today = datetime.date.today().strftime("%d/%m/%Y")

    cursor.execute("SELECT task_name, time_spent FROM tasks WHERE date = ?", (today,))
    tasks = [{"task_name": row[0], "time_spent": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return jsonify({"tasks": tasks})

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 8392506036798c45e4b9c32f8abd1b1b9d762472
