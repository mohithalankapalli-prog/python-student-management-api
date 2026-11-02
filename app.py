
from flask import Flask, request, jsonify
import sqlite3
from functools import wraps

app = Flask(__name__)

API_KEY = "Mohitha123"

# Database connection
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create database table
with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)

# API Authentication
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = request.headers.get("x-api-key")

        if key != API_KEY:
            return jsonify({"error": "Unauthorized access"}), 401

        return func(*args, **kwargs)
    return wrapper

# Home route
@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Student Management API"
    })

# CREATE student
@app.route("/students", methods=["POST"])
@authenticate
def add_student():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    course = data.get("course")
    email = data.get("email")

    if not all([name, course, email]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO students (name, course, email) VALUES (?, ?, ?)",
                (name, course, email)
            )

        return jsonify({"message": "Student added successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

# READ all students
@app.route("/students", methods=["GET"])
@authenticate
def get_students():
    with get_db() as conn:
        students = conn.execute(
            "SELECT * FROM students"
        ).fetchall()

    return jsonify([dict(row) for row in students])

# UPDATE student
@app.route("/students/<int:id>", methods=["PUT"])
@authenticate
def update_student(id):
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    course = data.get("course")
    email = data.get("email")

    if not all([name, course, email]):
        return jsonify({"error": "All fields are required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE students SET name=?, course=?, email=? WHERE id=?",
            (name, course, email, id)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student updated successfully"})

# DELETE student
@app.route("/students/<int:id>", methods=["DELETE"])
@authenticate
def delete_student(id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE id=?", (id,)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)
