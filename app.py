from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from activities import activities

app = Flask(__name__)

# Store submitted logs temporarily in memory
activity_logs = []

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        activities=activities,
        logs=activity_logs,
        edit_log=None,  # Not editing by default
        edit_id=None
    )

@app.route("/log", methods=["POST"])
def log_activity():
    start_time_str = request.form.get("start_time")
    finish_time_str = request.form.get("finish_time")
    
    # Calculate duration dynamically from clock inputs
    actual_duration = 0.0
    if start_time_str and finish_time_str:
        try:
            fmt = "%H:%M"
            t1 = datetime.strptime(start_time_str, fmt)
            t2 = datetime.strptime(finish_time_str, fmt)
            
            # Find total difference in hours
            tdelta = t2 - t1
            total_seconds = tdelta.total_seconds()
            
            # Handle overnight shifts gracefully if finish time is past midnight
            if total_seconds < 0:
                total_seconds += 86400 # Seconds in a day
                
            actual_duration = round(total_seconds / 3600.0, 2)
        except ValueError:
            actual_duration = 0.0

    log = {
        "activity_code": request.form.get("activity_code"),
        "actual_workers": request.form.get("actual_workers"),
        "start_time": start_time_str,
        "finish_time": finish_time_str,
        "actual_duration": actual_duration,
        "completion_percentage": request.form.get("completion_percentage"),
        "quantity_done": request.form.get("quantity_done"),
        "quantity_unit": request.form.get("quantity_unit"),
        "notes": request.form.get("notes")
    }
    activity_logs.append(log)
    return redirect(url_for('index'))

@app.route("/delete/<int:log_id>")
def delete_log(log_id):
    if 0 <= log_id < len(activity_logs):
        activity_logs.pop(log_id)
    return redirect(url_for('index'))

@app.route("/edit/<int:log_id>", methods=["GET", "POST"])
def edit_log(log_id):
    if log_id < 0 or log_id >= len(activity_logs):
        return redirect(url_for('index'))

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

        activity_logs[log_id] = {
            "activity_code": request.form.get("activity_code"),
            "actual_workers": request.form.get("actual_workers"),
            "start_time": start_time_str,
            "finish_time": finish_time_str,
            "actual_duration": actual_duration,
            "completion_percentage": request.form.get("completion_percentage"),
            "quantity_done": request.form.get("quantity_done"),
            "quantity_unit": request.form.get("quantity_unit"),
            "notes": request.form.get("notes")
        }
        return redirect(url_for('index'))

    return render_template(
        "index.html",
        activities=activities,
        logs=activity_logs,
        edit_log=activity_logs[log_id],
        edit_id=log_id
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)