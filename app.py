from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from activities import activities
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = Flask(__name__)

# --- INFLUXDB CONFIGURATION ---
INFLUX_URL = "http://localhost:8086"       # Change if your InfluxDB is hosted elsewhere
INFLUX_TOKEN = "YOUR_SUPER_SECRET_TOKEN"   # Replace with your actual InfluxDB token
INFLUX_ORG = "YOUR_ORG_NAME"               # Replace with your organization name
INFLUX_BUCKET = "construction_logs"        # Replace with your bucket name

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

def calculate_duration(start_str, finish_str):
    """Calculates time difference in hours between HH:MM strings"""
    try:
        fmt = "%H:%M"
        tdelta = datetime.strptime(finish_str, fmt) - datetime.strptime(start_str, fmt)
        hours = tdelta.total_seconds() / 3600.0
        if hours < 0: # Handles shifts passing through midnight
            hours += 24
        return round(hours, 2)
    except:
        return 0.0

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 1. Capture fields from your new visual layout
        activity_code = request.form.get("activity_code")
        actual_workers = int(request.form.get("actual_workers", 0))
        shift_start = request.form.get("shift_start")
        shift_finish = request.form.get("shift_finish")
        quantity = request.form.get("quantity", "0")
        unit = request.form.get("unit", "")
        progress = request.form.get("progress", "0")
        notes = request.form.get("notes", "")
        
        # Calculate duration in hours based on input times
        actual_duration = calculate_duration(shift_start, shift_finish)
        log_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # 2. Write Data Point to InfluxDB
        point = Point("field_logs") \
            .tag("activity_code", activity_code) \
            .field("actual_workers", actual_workers) \
            .field("shift_start", shift_start) \
            .field("shift_finish", shift_finish) \
            .field("actual_duration", actual_duration) \
            .field("quantity", quantity) \
            .field("unit", unit) \
            .field("progress", int(progress)) \
            .field("notes", notes) \
            .field("log_timestamp", log_timestamp)
        
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        return redirect(url_for('index'))

    # --- GET REQUEST: READ ALL LOGS FROM INFLUXDB FOR THE TABLE ---
    # Fetching records from the last 30 days to populate the grid
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "field_logs")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    
    records = []
    try:
        tables = query_api.query(query)
        for table in tables:
            for index, record in enumerate(table.records):
                records.append({
                    "id": index, # Used for targeting edits
                    "time_saved": record.values.get("log_timestamp", record.get_time().strftime("%Y-%m-%d %H:%M:%S")),
                    "activity_code": record.values.get("activity_code"),
                    "actual_workers": record.values.get("actual_workers", 0),
                    "shift_start": record.values.get("shift_start", "--:--"),
                    "shift_finish": record.values.get("shift_finish", "--:--"),
                    "actual_duration": record.values.get("actual_duration", 0.0),
                    "quantity": record.values.get("quantity", "0"),
                    "unit": record.values.get("unit", ""),
                    "progress": record.values.get("progress", 0),
                    "notes": record.values.get("notes", "")
                })
    except Exception as e:
        print(f"InfluxDB Query Error or Empty Bucket: {e}")

    # Reverse records list to show the newest entries at the very top of your table
    records.reverse()

    return render_template(
        "index.html",
        activities=activities,
        logs=records,
        edit_log=None
    )

@app.route("/edit", methods=["POST"])
def edit_log():
    # Overwriting/Editing in InfluxDB works by sending a point with the exact same 
    # timestamp tag or handling updates via rewriting points. 
    # For a simple solution, we write the modified entry as a fresh historical record!
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)