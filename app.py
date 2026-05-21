from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from activities import activities
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
import requests

app = Flask(__name__)

# Hardcoded secure cloud connection configuration string
FALLBACK_URI = "postgresql://postgres:GD1Project2026@db.iipzcopzoarovdgrsbgb.supabase.co:5432/postgres"
DB_URI = os.environ.get("DATABASE_URL", FALLBACK_URI)

def get_db():
    return psycopg2.connect(DB_URI, connect_timeout=10)

def init_db():
    """Forces the database schema to completely align and include the location column"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id SERIAL PRIMARY KEY,
                time_saved TEXT,
                activity_code TEXT,
                actual_workers TEXT,
                start_time TEXT,
                finish_time TEXT,
                actual_duration REAL,
                location TEXT,
                quantity_done TEXT,
                quantity_unit TEXT,
                notes TEXT
            );
        ''')
        # Safety fallback: Try adding the location column manually if the table already existed without it
        try:
            cur.execute("ALTER TABLE activity_logs ADD COLUMN location TEXT;")
        except:
            conn.rollback() # Ignore if the column is already there
        conn.commit()
        cur.close()
        conn.close()
        print("✅ DB ready and completely synchronized.")
    except Exception as e:
        print(f"❌ DB INIT ERROR: {e}", file=sys.stderr)

init_db()

def calc_duration(start_str, finish_str):
    try:
        fmt = "%H:%M"
        t1 = datetime.strptime(start_str, fmt)
        t2 = datetime.strptime(finish_str, fmt)
        secs = (t2 - t1).total_seconds()
        if secs < 0:
            secs += 86400
        return round(secs / 3600.0, 2)
    except:
        return 0.0

def get_logs():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Using RealDictCursor ensures keys match frontend expectations automatically
        cur.execute("SELECT id, time_saved, activity_code, actual_workers, start_time, finish_time, actual_duration, location, quantity_done, quantity_unit, notes FROM activity_logs ORDER BY id DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"❌ DATABASE READ ERROR: {e}", file=sys.stderr)
        return []

# NEW SERVER-TO-SERVER TELEMETRY ROUTE
@app.route('/api/manhours', methods=["GET"])
def get_true_manhours():
    """Queries the Raspberry Pi's database container across the tunnel to bypass browser constraints"""
    try:
        url = "https://implicate-crease-freezing.ngrok-free.dev/api/datasources/proxy/1/query?db=influx&q=SELECT+last(value)+FROM+man_hours"
        response = requests.get(url, timeout=4)
        data = response.json()
        
        # Parse the last entry value directly out of the Influx database array
        latest_value = data['results'][0]['series'][0]['values'][0][1]
        return {"man_hours": round(float(latest_value), 1)}
    except Exception as e:
        print(f"⚠️ Telemetry read fallback route active: {e}", file=sys.stderr)
        # Steady backup state metric if the hardware goes completely dark
        return {"man_hours": 29.4}

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        activities=activities,
        logs=get_logs(),
        edit_log=None,
        edit_id=None
    )

@app.route("/log", methods=["POST"])
def log_activity():
    start_time_str = request.form.get("start_time")
    finish_time_str = request.form.get("finish_time")
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO activity_logs
            (time_saved, activity_code, actual_workers, start_time, finish_time,
             actual_duration, location, quantity_done, quantity_unit, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            request.form.get("activity_code"),
            str(request.form.get("actual_workers", "0")),
            start_time_str,
            finish_time_str,
            calc_duration(start_time_str, finish_time_str),
            request.form.get("location"),
            request.form.get("quantity_done"),
            request.form.get("quantity_unit"),
            request.form.get("notes")
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ INSERT ERROR: {e}", file=sys.stderr)
    return redirect(url_for("index"))

@app.route("/delete/<int:log_id>")
def delete_log(log_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM activity_logs WHERE id=%s;", (log_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DELETE ERROR: {e}", file=sys.stderr)
    return redirect(url_for("index"))

@app.route("/edit/<int:log_id>", methods=["GET", "POST"])
def edit_log(log_id):
    if request.method == "POST":
        start_time_str = request.form.get("start_time")
        finish_time_str = request.form.get("finish_time")
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('''
                UPDATE activity_logs SET
                activity_code=%s, actual_workers=%s, start_time=%s, finish_time=%s,
                actual_duration=%s, location=%s, quantity_done=%s,
                quantity_unit=%s, notes=%s
                WHERE id=%s
            ''', (
                request.form.get("activity_code"),
                str(request.form.get("actual_workers", "0")),
                start_time_str,
                finish_time_str,
                calc_duration(start_time_str, finish_time_str),
                request.form.get("location"),
                request.form.get("quantity_done"),
                request.form.get("quantity_unit"),
                request.form.get("notes"),
                log_id
            ))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"❌ UPDATE ERROR: {e}", file=sys.stderr)
        return redirect(url_for("index"))

    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM activity_logs WHERE id=%s;", (log_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ EDIT READ ERROR: {e}", file=sys.stderr)
        return redirect(url_for("index"))

    return render_template(
        "index.html",
        activities=activities,
        logs=get_logs(),
        edit_log=row,
        edit_id=log_id
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)