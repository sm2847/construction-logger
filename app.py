from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

# Import the InfluxDB client modules
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Import your static baseline programming data dictionary
from activities import activities

app = Flask(__name__)

# ---------------------------------------------------------
# PERSISTENT TIME-SERIES DATABASE CONFIGURATION NODES
# ---------------------------------------------------------
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"  # Your InfluxDB Cloud instance URL
INFLUX_TOKEN = "YOUR_ACTUAL_INFLUXDB_SECRET_TOKEN_STRING"     # Your secure security token string
INFLUX_ORG = "YOUR_ORGANIZATION_EMAIL_OR_NAME"
INFLUX_BUCKET = "construction_metrics"

# Initialize global InfluxDB communication drivers
db_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = db_client.write_api(write_options=SYNCHRONOUS)
query_api = db_client.query_api()


@app.route("/", methods=["GET"])
def index():
    activity_logs = []
    
    # Clean Query: Fetch fields stored over the past 30 days
    flux_query = f'''
    from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -30d)
        |> filter(fn: (r) => r["_measurement"] == "field_log_events")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time"], desc: true)
    '''
    
    try:
        result = query_api.query(org=INFLUX_ORG, query=flux_query)
        for table in result:
            for record in table.records:
                # Capture the precise timestamp stored natively by the database engine
                raw_time = record.get_time()
                # Format into a clean, human-readable layout option
                formatted_timestamp = raw_time.strftime("%d %b %Y, %H:%M:%S")
                
                # Extract values safely while defaulting to clean alternative types
                activity_logs.append({
                    "timestamp": formatted_timestamp,
                    "activity_code": record.values.get("activity_code"),
                    "actual_workers": record.values.get("actual_workers", 0),
                    "start_time": record.values.get("start_time", "--:--"),
                    "finish_time": record.values.get("finish_time", "--:--"),
                    "actual_duration": record.values.get("actual_duration", 0.0),
                    "quantity_done": record.values.get("quantity_done", 0.0),
                    "quantity_unit": record.values.get("quantity_unit", ""),
                    "completion_percentage": record.values.get("completion_percentage", 0),
                    "notes": record.values.get("notes", "")
                })
    except Exception as e:
        print(f"⚠️ Database query skipped or empty bucket configuration: {e}")
        activity_logs = []

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
    activity_code = request.form.get("activity_code")
    
    # Calculate duration spent dynamically via standard clock parameters
    actual_duration = 0.0
    if start_time_str and finish_time_str:
        try:
            fmt = "%H:%M"
            t1 = datetime.strptime(start_time_str, fmt)
            t2 = datetime.strptime(finish_time_str, fmt)
            tdelta = t2 - t1
            total_seconds = tdelta.total_seconds()
            
            # Accommodate any night-shift crossovers cleanly
            if total_seconds < 0:
                total_seconds += 86400
                
            actual_duration = round(total_seconds / 3600.0, 2)
        except ValueError:
            actual_duration = 0.0

    # Build a clean time-series telemetry metrics object point
    point = Point("field_log_events") \
        .field("activity_code", str(activity_code)) \
        .field("actual_workers", int(request.form.get("actual_workers") or 0)) \
        .field("start_time", str(start_time_str)) \
        .field("finish_time", str(finish_time_str)) \
        .field("actual_duration", float(actual_duration)) \
        .field("quantity_done", float(request.form.get("quantity_done") or 0.0)) \
        .field("quantity_unit", str(request.form.get("quantity_unit") or "")) \
        .field("completion_percentage", int(request.form.get("completion_percentage") or 0)) \
        .field("notes", str(request.form.get("notes") or "")) \
        .time(datetime.utcnow(), WritePrecision.NS)  # Exact automated generation time stamp

    try:
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    except Exception as e:
        print(f"⚠️ Database write execution issue encountered: {e}")

    return redirect(url_for('index'))


@app.route("/delete/<int:log_id>")
def delete_log(log_id):
    # Relational redirects process cleanly for displaying persistent rows
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)