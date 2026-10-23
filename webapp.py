
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import sqlite3
from pathlib import Path

app = Flask(__name__, static_folder="static")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "careloop.db"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                reminder_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)


def medicine_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "reminder_time": row["reminder_time"],
        "status": row["status"]
    }


@app.get("/")
def home():
    return send_from_directory(str(BASE_DIR / "static"), "index.html")


@app.get("/api/medicines")
def list_medicines():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM medicines ORDER BY id"
        ).fetchall()

    return jsonify([medicine_to_dict(row) for row in rows])


@app.post("/api/medicines")
def add_medicine():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    reminder_time = str(data.get("reminder_time", "")).strip()

    if not name or not reminder_time:
        return jsonify({
            "error": "Medicine name and time are required."
        }), 400

    if len(name) > 100:
        return jsonify({
            "error": "Medicine name must be 100 characters or fewer."
        }), 400

    try:
        datetime.strptime(reminder_time, "%H:%M")
    except ValueError:
        return jsonify({
            "error": "Use 24-hour HH:MM time format."
        }), 400

    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO medicines (name, reminder_time, status) "
            "VALUES (?, ?, 'Pending')",
            (name, reminder_time)
        )

        row = db.execute(
            "SELECT * FROM medicines WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

    return jsonify(medicine_to_dict(row)), 201


@app.patch("/api/medicines/<int:medicine_id>")
def update_medicine(medicine_id):
    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).title()

    if status not in ("Taken", "Missed"):
        return jsonify({
            "error": "Status must be Taken or Missed."
        }), 400

    with get_db() as db:
        cursor = db.execute(
            "UPDATE medicines SET status = ? WHERE id = ?",
            (status, medicine_id)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Medicine not found."}), 404

        row = db.execute(
            "SELECT * FROM medicines WHERE id = ?",
            (medicine_id,)
        ).fetchone()

    return jsonify(medicine_to_dict(row))


@app.delete("/api/medicines/<int:medicine_id>")
def delete_medicine(medicine_id):
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM medicines WHERE id = ?",
            (medicine_id,)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Medicine not found."}), 404

    return jsonify({"message": "Medicine removed."})


initialize_database()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
