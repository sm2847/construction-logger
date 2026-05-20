from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from activities import activities
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

app = Flask(__name__)

# --- SECURE DATABASE INJECTION ---
# The exclamation mark in your password has been encoded to %21 to prevent connection crashes.
DB_URI = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:Pass1234%21GD12026@db.iipzcopzoarovdgrsbgb.supabase.co:5432/postgres"
)

def get_db_connection():
    # Connects to Supabase Cloud with a 5-second failure timeout guard
    conn = psycopg2.connect(DB_URI, connect_timeout=5)
    return conn

def init_db():
    """Initializes the underlying PostgreSQL schema structure if missing"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS field_logs (
                id SERIAL PRIMARY KEY,
                time_saved TEXT NOT NULL,
                activity_code TEXT NOT NULL,
                actual_workers INTEGER NOT NULL,
                shift_start TEXT NOT NULL,
                shift_finish TEXT NOT NULL,
                actual_duration REAL NOT NULL,
                quantity TEXT NOT NULL,
                unit TEXT NOT NULL,
                progress INTEGER NOT NULL,
                notes TEXT
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database connection successful and tables initialized.")
    except Exception as e:
        print(f"❌ DATABASE INITIALIZATION ERROR ON STARTUP: {e}", file=sys.stderr)

# Run database schema auto-check on startup
init_db()

def calculate_duration(start_str, finish_str):
    """Calculates time difference in decimal hours across shift timestamps"""
    try:
        fmt = "%H:%M"
        tdelta = datetime.strptime(finish_str, fmt) - datetime.strptime(start_str, fmt)
        hours = tdelta.total_seconds() / 3600.0
        if hours < 0: 
            hours += 24
        return round(hours, 2)
    except:
        return 0.0

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        activity_code = request.form.get("activity_code")
        actual_workers = int(request.form.get("actual_workers", 0))
        shift_start = request.form.get("shift_start")
        shift_finish = request.form.get("shift_finish")
        quantity = request.form.get("quantity", "0")
        unit = request.form.get("unit", "")
        progress = request.form.get("progress", "0")
        notes = request.form.get("notes", "")
        
        actual_duration = calculate_duration(shift_start, shift_finish)
        log_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO field_logs (time_saved, activity_code, actual_workers, shift_start, shift_finish, actual_duration, quantity, unit, progress, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (log_timestamp, activity_code, actual_workers, shift_start, shift_finish, actual_duration, quantity, unit, int(progress), notes))
            conn.commit()
            cur.close()
            conn.close()
            print("🎉 Log successfully committed to Supabase!")
        except Exception as e:
            print(f"❌ CRITICAL STORAGE ERROR: {e}", file=sys.stderr)

        return redirect(url_for('index'))

    # GET Request: Fetch logs matrix to draw UI grid
    records = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM field_logs ORDER BY id DESC;')
        records = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR LOADING LOG MATRIX: {e}", file=sys.stderr)

    return render_template(
        "index.html",
        activities=activities,
        logs=records,
        edit_log=None
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)