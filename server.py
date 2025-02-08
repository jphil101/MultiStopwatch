from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import threading
import datetime
import time

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

DB_FILE = "tasks.db"

# Create DB table if not exists
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            task_name TEXT,
            duration TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()  # Initialize DB when server starts

# ✅ Root route for testing
@app.route("/")
def home():
    return "Backend is running!"

# ✅ Get all tasks for today
@app.route("/tasks", methods=["GET"])
def get_tasks():
    today = datetime.date.today().strftime("%d/%m/%Y")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT task_name, duration FROM tasks WHERE date = ?", (today,))
    tasks = cursor.fetchall()
    conn.close()
    return jsonify([{"task_name": t[0], "duration": t[1]} for t in tasks])

# ✅ Save a task (called when stopwatch updates)
@app.route("/save_task", methods=["POST"])
def save_task():
    data = request.json
    task_name = data.get("task_name")
    duration = data.get("duration")
    today = datetime.date.today().strftime("%d/%m/%Y")

    if not task_name or not duration:
        return jsonify({"error": "Missing task_name or duration"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (date, task_name, duration) VALUES (?, ?, ?)", (today, task_name, duration))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task saved!"})

# ✅ Manual sweep (move all today's tasks to DB)
@app.route("/manual_sweep", methods=["POST"])
def manual_sweep():
    today = datetime.date.today().strftime("%d/%m/%Y")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE date = ?", (today,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Manual sweep completed!"})

# ✅ Auto-sweep at midnight
def auto_sweep():
    while True:
        now = datetime.datetime.now()
        midnight = datetime.datetime.combine(now.date(), datetime.time(0, 0)) + datetime.timedelta(days=1)
        seconds_until_midnight = (midnight - now).total_seconds()
        time.sleep(seconds_until_midnight)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        today = datetime.date.today().strftime("%d/%m/%Y")
        cursor.execute("DELETE FROM tasks WHERE date = ?", (today,))
        conn.commit()
        conn.close()

        print("Auto-sweep completed at midnight.")

# Start auto-sweep thread
threading.Thread(target=auto_sweep, daemon=True).start()

# ✅ Run server
if __name__ == "__main__":
    app.run(debug=True)
