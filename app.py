from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from activities import activities
import psycopg2
import sys
import os

app = Flask(__name__)

# --- SECURE CLOUD DATABASE CONFIGURATION ---
# The password's exclamation mark is URL-encoded as %21 to prevent connection crashes on Render
FALLBACK_URI = "postgresql://postgres:Pass1234%21GD12026@db.iipzcopzoarovdgrsbgb.supabase.co:5432/postgres"
DB_URI = os.environ.get("DATABASE_URL", FALLBACK_URI)

def get_db_connection():
    """Establishes an active pipeline to your Supabase Cloud Database"""
    return psycopg2.connect(DB_URI, connect_timeout=10)

def init_db():
    """Creates the structural table inside Supabase automatically if missing"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS field_logs (
                id SERIAL PRIMARY KEY,
                time_saved TEXT NOT NULL,
                activity_code TEXT NOT NULL,
                actual_workers TEXT NOT NULL,
                shift_start TEXT NOT NULL,
                shift_finish TEXT NOT NULL,
                actual_duration REAL NOT NULL,
                quantity_done TEXT NOT NULL,
                quantity_unit TEXT NOT NULL,
                completion_percentage TEXT NOT NULL,
                notes TEXT
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Supabase cloud database schema initialized and active.")
    except Exception as e:
        print(f"❌ DATABASE INITIALIZATION ERROR: {e}", file=sys.stderr)

# Run database layout verification checks instantly on application startup
init_db()

def calculate_duration(start_str, finish_str):
    """Calculates time difference in decimal hours from HTML time pickers"""
    if start_str and finish_str:
        try:
            fmt = "%H:%M"
            t1 = datetime.strptime(start_str, fmt)
            t2 = datetime.strptime(finish_str, fmt)
            
            tdelta = t2 - t1
            total_seconds = tdelta.total_seconds()
            
            # Handle overnight shifts gracefully if finish time passes midnight
            if total_seconds < 0:
                total_seconds += 86400
                
            return round(total_seconds / 3600.0, 2)
        except ValueError:
            return 0.0
    return 0.0

@app.route("/", methods=["GET"])
def index():
    # Fetch active logged entries out of Supabase cloud database
    records = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, time_saved, activity_code, actual_workers, shift_start, shift_finish, actual_duration, quantity_done, quantity_unit, completion_percentage, notes FROM field_logs ORDER BY id DESC;')
        rows = cur.fetchall()
        
        for row in rows:
            records.append({
                "id": row[0],
                "time_saved": row[1],
                "activity_code": row[2],
                "actual_workers": row[3],
                "start_time": row[4],
                "finish_time": row[5],
                "actual_duration": row[6],
                "quantity_done": row[7],
                "quantity_unit": row[8],
                "completion_percentage": row[9],
                "notes": row[10]
            })
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR READING FROM SUPABASE MATRIX: {e}", file=sys.stderr)

    return render_template(
        "index.html",
        activities=activities,
        logs=records,
        edit_log=None,
        edit_id=None
    )

@app.route("/log", methods=["POST"])
def log_activity():
    start_time_str = request.form.get("start_time")
    finish_time_str = request.form.get("finish_time")
    activity_code = request.form.get("activity_code")
    actual_workers = request.form.get("actual_workers")
    completion_percentage = request.form.get("completion_percentage")
    quantity_done = request.form.get("quantity_done")
    quantity_unit = request.form.get("quantity_unit")
    notes = request.form.get("notes")
    
    actual_duration = calculate_duration(start_time_str, finish_time_str)
    log_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save log entry straight to the cloud database
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO field_logs (time_saved, activity_code, actual_workers, shift_start, shift_finish, actual_duration, quantity_done, quantity_unit, completion_percentage, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (log_timestamp, activity_code, actual_workers, start_time_str, finish_time_str, actual_duration, quantity_done, quantity_unit, completion_percentage, notes))
        conn.commit()
        cur.close()
        conn.close()
        print("🎉 Log written to Supabase cloud successfully!")
    except Exception as e:
        print(f"❌ ERROR WRITING TO DATABASE LAYER: {e}", file=sys.stderr)

    return redirect(url_for('index'))

@app.route("/delete/<int:log_id>")
def delete_log(log_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM field_logs WHERE id=%s;', (log_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR DELETING ROW RECORD: {e}", file=sys.stderr)
    return redirect(url_for('index'))

@app.route("/edit/<int:log_id>", methods=["GET", "POST"])
def edit_log(log_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        start_time_str = request.form.get("start_time")
        finish_time_str = request.form.get("finish_time")
        activity_code = request.form.get("activity_code")
        actual_workers = request.form.get("actual_workers")
        completion_percentage = request.form.get("completion_percentage")
        quantity_done = request.form.get("quantity_done")
        quantity_unit = request.form.get("quantity_unit")
        notes = request.form.get("notes")
        
        actual_duration = calculate_duration(start_time_str, finish_time_str)

        try:
            cur.execute('''
                UPDATE field_logs 
                SET activity_code=%s, actual_workers=%s, shift_start=%s, shift_finish=%s, actual_duration=%s, quantity_done=%s, quantity_unit=%s, completion_percentage=%s, notes=%s
                WHERE id=%s
            ''', (activity_code, actual_workers, start_time_str, finish_time_str, actual_duration, quantity_done, quantity_unit, completion_percentage, notes, log_id))
            conn.commit()
        except Exception as e:
            print(f"❌ ERROR UPDATING DATABASE RECORD: {e}", file=sys.stderr)
            
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    # GET Request: Pull the single active record row to load input fields
    cur.execute('SELECT id, activity_code, actual_workers, shift_start, shift_finish, quantity_done, quantity_unit, completion_percentage, notes FROM field_logs WHERE id=%s;', (log_id,))
    row = cur.fetchone()
    
    edit_log_data = None
    if row:
        edit_log_data = {
            "id": row[0],
            "activity_code": row[1],
            "actual_workers": row[2],
            "start_time": row[3],
            "finish_time": row[4],
            "quantity_done": row[5],
            "quantity_unit": row[6],
            "completion_percentage": row[7],
            "notes": row[8]
        }

    # Pull down remaining database records to render background log tracking dashboard layout
    cur.execute('SELECT id, time_saved, activity_code, actual_workers, shift_start, shift_finish, actual_duration, quantity_done, quantity_unit, completion_percentage, notes FROM field_logs ORDER BY id DESC;')
    rows = cur.fetchall()
    records = []
    for r in rows:
        records.append({
            "id": r[0], "time_saved": r[1], "activity_code": r[2], "actual_workers": r[3],
            "start_time": r[4], "finish_time": r[5], "actual_duration": r[6],
            "quantity_done": r[7], "quantity_unit": r[8], "completion_percentage": r[9], "notes": r[10]
        })

    cur.close()
    conn.close()
    
    return render_template(
        "index.html",
        activities=activities,
        logs=records,
        edit_log=edit_log_data,
        edit_id=log_id
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)