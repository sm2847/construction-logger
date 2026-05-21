from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from activities import activities
import psycopg2
import sys
import os

app = Flask(__name__)

# --- SECURE PERSISTENT CLOUD CONFIGURATION ---
FALLBACK_URI = "postgresql://postgres:Pass1234%21GD12026@db.iipzcopzoarovdgrsbgb.supabase.co:5432/postgres"
DB_URI = os.environ.get("DATABASE_URL", FALLBACK_URI)

def get_db_connection():
    return psycopg2.connect(DB_URI, connect_timeout=10)

def init_db():
    """Verifies table topology configuration natively on startup"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS field_logs (
                id SERIAL PRIMARY KEY,
                activity_code TEXT NOT NULL,
                actual_workers TEXT NOT NULL,
                start_time TEXT NOT NULL,
                finish_time TEXT NOT NULL,
                actual_duration REAL NOT NULL,
                completion_percentage TEXT NOT NULL,
                quantity TEXT NOT NULL,
                unit TEXT NOT NULL,
                notes TEXT
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Supabase cloud tracking schema active.")
    except Exception as e:
        print(f"❌ DATABASE INITIALIZATION ERROR: {e}", file=sys.stderr)

init_db()

def get_all_logs():
    """Fetches records out of Supabase mapping columns directly to template targets"""
    records = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, activity_code, actual_workers, start_time, finish_time, actual_duration, completion_percentage, quantity, unit, notes FROM field_logs ORDER BY id ASC;')
        rows = cur.fetchall()
        for row in rows:
            records.append({
                "id": row[0],
                "activity_code": row[1],
                "actual_workers": row[2],
                "start_time": row[3],
                "finish_time": row[4],
                "actual_duration": row[5],
                "completion_percentage": row[6],
                "quantity_done": row[7],    # Maps column 'quantity' to frontend key 'quantity_done'
                "quantity_unit": row[8],    # Maps column 'unit' to frontend key 'quantity_unit'
                "notes": row[9]
            })
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR LOADING LOGS MATRIX OVER RELATIONAL DISK: {e}", file=sys.stderr)
    return records

@app.route("/", methods=["GET"])
def index():
    activity_logs = get_all_logs()
    return render_template(
        "index.html",
        activities=activities,
        logs=activity_logs,
        edit_log=None,
        edit_id=None
    )

@app.route("/log", methods=["POST"])
def log_activity():
    start_time_str = request.form.get("start_time")
    finish_time_str = request.form.get("finish_time")
    
    actual_duration = 0.0
    if start_time_str and finish_time_str:
        try:
            fmt = "%H:%M"
            t1 = datetime.strptime(start_time_str, fmt)
            t2 = datetime.strptime(finish_time_str, fmt)
            tdelta = t2 - t1
            total_seconds = tdelta.total_seconds()
            if total_seconds < 0:
                total_seconds += 86400
            actual_duration = round(total_seconds / 3600.0, 2)
        except ValueError:
            actual_duration = 0.0

    activity_code = request.form.get("activity_code")
    actual_workers = request.form.get("actual_workers")
    completion_percentage = request.form.get("completion_percentage")
    quantity_done = request.form.get("quantity_done")
    quantity_unit = request.form.get("quantity_unit")
    notes = request.form.get("notes")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Saves frontend variables safely straight into the verified 'quantity' and 'unit' database rows
        cur.execute('''
            INSERT INTO field_logs (activity_code, actual_workers, start_time, finish_time, actual_duration, completion_percentage, quantity, unit, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (activity_code, actual_workers, start_time_str, finish_time_str, actual_duration, completion_percentage, quantity_done, quantity_unit, notes))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR PERSISTING NEW FIELD LOG ENTRY: {e}", file=sys.stderr)

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
        print(f"❌ ERROR REMOVING SPECIFIED TARGET ROW: {e}", file=sys.stderr)
    return redirect(url_for('index'))

@app.route("/edit/<int:log_id>", methods=["GET", "POST"])
def edit_log(log_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        start_time_str = request.form.get("start_time")
        finish_time_str = request.form.get("finish_time")
        
        actual_duration = 0.0
        if start_time_str and finish_time_str:
            try:
                fmt = "%H:%M"
                t1 = datetime.strptime(start_time_str, fmt)
                t2 = datetime.strptime(finish_time_str, fmt)
                tdelta = t2 - t1
                total_seconds = tdelta.total_seconds()
                if total_seconds < 0:
                    total_seconds += 86400
                actual_duration = round(total_seconds / 3600.0, 2)
            except ValueError:
                actual_duration = 0.0

        activity_code = request.form.get("activity_code")
        actual_workers = request.form.get("actual_workers")
        completion_percentage = request.form.get("completion_percentage")
        quantity_done = request.form.get("quantity_done")
        quantity_unit = request.form.get("quantity_unit")
        notes = request.form.get("notes")

        try:
            cur.execute('''
                UPDATE field_logs 
                SET activity_code=%s, actual_workers=%s, start_time=%s, finish_time=%s, actual_duration=%s, completion_percentage=%s, quantity=%s, unit=%s, notes=%s
                WHERE id=%s
            ''', (activity_code, actual_workers, start_time_str, finish_time_str, actual_duration, completion_percentage, quantity_done, quantity_unit, notes, log_id))
            conn.commit()
        except Exception as e:
            print(f"❌ ERROR EXECUTING UPDATE STRATUM OPERATION: {e}", file=sys.stderr)
            
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    cur.execute('SELECT id, activity_code, actual_workers, start_time, finish_time, actual_duration, completion_percentage, quantity, unit, notes FROM field_logs WHERE id=%s;', (log_id,))
    row = cur.fetchone()
    
    target_edit_log = None
    if row:
        target_edit_log = {
            "id": row[0],
            "activity_code": row[1],
            "actual_workers": row[2],
            "start_time": row[3],
            "finish_time": row[4],
            "actual_duration": row[5],
            "completion_percentage": row[6],
            "quantity_done": row[7],
            "quantity_unit": row[8],
            "notes": row[9]
        }

    cur.close()
    conn.close()

    activity_logs = get_all_logs()
    return render_template(
        "index.html",
        activities=activities,
        logs=activity_logs,
        edit_log=target_edit_log,
        edit_id=log_id
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)