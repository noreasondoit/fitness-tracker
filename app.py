import sqlite3
import json
import os
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, g, send_from_directory

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracker.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS weight_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            weight_kg REAL NOT NULL,
            note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            description TEXT NOT NULL,
            calories INTEGER DEFAULT 0,
            protein_g REAL DEFAULT 0,
            carbs_g REAL DEFAULT 0,
            fat_g REAL DEFAULT 0,
            note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            name TEXT DEFAULT '',
            exercises TEXT DEFAULT '[]',
            duration_min INTEGER DEFAULT 0,
            note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS mobility_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            area TEXT NOT NULL,
            exercise TEXT NOT NULL,
            duration_min INTEGER DEFAULT 0,
            pain_level INTEGER DEFAULT 0,
            side TEXT DEFAULT 'both',
            note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS ankle_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER DEFAULT 3,
            reps INTEGER DEFAULT 10,
            difficulty INTEGER DEFAULT 0,
            note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS body_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            weight_kg REAL,
            neck_cm REAL,
            shoulders_cm REAL,
            chest_cm REAL,
            biceps_l_cm REAL,
            biceps_r_cm REAL,
            forearm_l_cm REAL,
            forearm_r_cm REAL,
            waist_cm REAL,
            hips_cm REAL,
            thigh_l_cm REAL,
            thigh_r_cm REAL,
            calf_l_cm REAL,
            calf_r_cm REAL,
            ankle_l_cm REAL,
            ankle_r_cm REAL,
            note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general'
        );
    """)
    db.commit()
    db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


# ---- WEIGHT API ----
@app.route("/api/weight", methods=["GET", "POST"])
def api_weight():
    db = get_db()
    if request.method == "POST":
        data = request.json
        db.execute(
            "INSERT OR REPLACE INTO weight_log (date, weight_kg, note) VALUES (?, ?, ?)",
            (data["date"], data["weight_kg"], data.get("note", ""))
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT * FROM weight_log ORDER BY date DESC LIMIT 90").fetchall()
    return jsonify([dict(r) for r in rows])


# ---- MEALS API ----
@app.route("/api/meals", methods=["GET", "POST"])
def api_meals():
    db = get_db()
    if request.method == "POST":
        data = request.json
        db.execute(
            "INSERT INTO meals (date, meal_type, description, calories, protein_g, carbs_g, fat_g, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data["date"], data["meal_type"], data["description"],
             data.get("calories", 0), data.get("protein_g", 0),
             data.get("carbs_g", 0), data.get("fat_g", 0), data.get("note", ""))
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT * FROM meals ORDER BY date DESC, id DESC LIMIT 200").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/meals/<int:meal_id>", methods=["DELETE"])
def api_delete_meal(meal_id):
    db = get_db()
    db.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    db.commit()
    return jsonify({"ok": True})


# ---- WORKOUTS API ----
@app.route("/api/workouts", methods=["GET", "POST"])
def api_workouts():
    db = get_db()
    if request.method == "POST":
        data = request.json
        db.execute(
            "INSERT OR REPLACE INTO workouts (date, name, exercises, duration_min, note) VALUES (?, ?, ?, ?, ?)",
            (data["date"], data.get("name", ""), json.dumps(data.get("exercises", [])),
             data.get("duration_min", 0), data.get("note", ""))
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT * FROM workouts ORDER BY date DESC LIMIT 90").fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["exercises"] = json.loads(d["exercises"])
        result.append(d)
    return jsonify(result)


# ---- MOBILITY API ----
@app.route("/api/mobility", methods=["GET", "POST"])
def api_mobility():
    db = get_db()
    if request.method == "POST":
        data = request.json
        db.execute(
            "INSERT INTO mobility_log (date, area, exercise, duration_min, pain_level, side, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data["date"], data["area"], data["exercise"],
             data.get("duration_min", 0), data.get("pain_level", 0),
             data.get("side", "both"), data.get("note", ""))
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT * FROM mobility_log ORDER BY date DESC, id DESC LIMIT 200").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/mobility/<int:log_id>", methods=["DELETE"])
def api_delete_mobility(log_id):
    db = get_db()
    db.execute("DELETE FROM mobility_log WHERE id = ?", (log_id,))
    db.commit()
    return jsonify({"ok": True})


# ---- ANKLE EXERCISES API ----
@app.route("/api/ankle", methods=["GET", "POST"])
def api_ankle():
    db = get_db()
    if request.method == "POST":
        data = request.json
        db.execute(
            "INSERT INTO ankle_exercises (date, exercise, sets, reps, difficulty, note) VALUES (?, ?, ?, ?, ?, ?)",
            (data["date"], data["exercise"], data.get("sets", 3),
             data.get("reps", 10), data.get("difficulty", 0), data.get("note", ""))
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT * FROM ankle_exercises ORDER BY date DESC, id DESC LIMIT 100").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/ankle/<int:log_id>", methods=["DELETE"])
def api_delete_ankle(log_id):
    db = get_db()
    db.execute("DELETE FROM ankle_exercises WHERE id = ?", (log_id,))
    db.commit()
    return jsonify({"ok": True})


# ---- MEASUREMENTS API ----
@app.route("/api/measurements", methods=["GET", "POST"])
def api_measurements():
    db = get_db()
    if request.method == "POST":
        data = request.json
        fields = [
            "date", "weight_kg", "neck_cm", "shoulders_cm", "chest_cm",
            "biceps_l_cm", "biceps_r_cm", "forearm_l_cm", "forearm_r_cm",
            "waist_cm", "hips_cm", "thigh_l_cm", "thigh_r_cm",
            "calf_l_cm", "calf_r_cm", "ankle_l_cm", "ankle_r_cm", "note"
        ]
        values = [data.get(f, None) for f in fields]
        placeholders = ",".join(["?" for _ in fields])
        db.execute(
            f"INSERT OR REPLACE INTO body_measurements ({','.join(fields)}) VALUES ({placeholders})",
            values
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT * FROM body_measurements ORDER BY date DESC LIMIT 30").fetchall()
    return jsonify([dict(r) for r in rows])


# ---- NOTES API ----
@app.route("/api/notes", methods=["GET", "POST"])
def api_notes():
    db = get_db()
    if request.method == "POST":
        data = request.json
        db.execute(
            "INSERT INTO notes (date, content, category) VALUES (?, ?, ?)",
            (data["date"], data["content"], data.get("category", "general"))
        )
        db.commit()
        return jsonify({"ok": True})
    rows = db.execute("SELECT * FROM notes ORDER BY date DESC, id DESC LIMIT 200").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def api_delete_note(note_id):
    db = get_db()
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return jsonify({"ok": True})


# ---- DAILY SUMMARY ----
@app.route("/api/summary/<string:dt>")
def api_summary(dt):
    db = get_db()
    meals = db.execute("SELECT SUM(calories) as cal, SUM(protein_g) as prot FROM meals WHERE date = ?", (dt,)).fetchone()
    mob = db.execute("SELECT SUM(duration_min) as dur FROM mobility_log WHERE date = ?", (dt,)).fetchone()
    ankle = db.execute("SELECT COUNT(*) as cnt FROM ankle_exercises WHERE date = ?", (dt,)).fetchone()
    w = db.execute("SELECT weight_kg FROM weight_log WHERE date = ?", (dt,)).fetchone()
    wo = db.execute("SELECT name, duration_min FROM workouts WHERE date = ?", (dt,)).fetchone()
    return jsonify({
        "calories": meals["cal"] or 0,
        "protein": round(meals["prot"] or 0, 1),
        "mobility_min": mob["dur"] or 0,
        "ankle_exercises": ankle["cnt"] or 0,
        "weight": round(w["weight_kg"], 1) if w and w["weight_kg"] else None,
        "workout": dict(wo) if wo else None
    })


if __name__ == "__main__":
    init_db()
    print("Fitness Tracker running at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
