from flask import Flask, render_template, request, redirect
from activities import activities

app = Flask(__name__)

# Store submitted logs temporarily
activity_logs = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        log = {
            "activity_code": request.form.get("activity_code"),
            "start_time": request.form.get("start_time"),
            "end_time": request.form.get("end_time"),
            "actual_workers": request.form.get("actual_workers"),
            "equipment": request.form.get("equipment"),
            "completed": request.form.get("completed"),
            "notes": request.form.get("notes")
        }
        activity_logs.append(log)
        return redirect("/")

    return render_template(
        "index.html",
        activities=activities,
        logs=activity_logs,
        edit_log=None  # Not editing by default
    )

@app.route("/delete/<int:log_id>")
def delete_log(log_id):
    if 0 <= log_id < len(activity_logs):
        activity_logs.pop(log_id)  # Remove log from list by its index
    return redirect("/")

@app.route("/edit/<int:log_id>", methods=["GET", "POST"])
def edit_log(log_id):
    if log_id < 0 or log_id >= len(activity_logs):
        return redirect("/")

    if request.method == "POST":
        # Update the existing log data with the new inputs
        activity_logs[log_id] = {
            "activity_code": request.form.get("activity_code"),
            "start_time": request.form.get("start_time"),
            "end_time": request.form.get("end_time"),
            "actual_workers": request.form.get("actual_workers"),
            "equipment": request.form.get("equipment"),
            "completed": request.form.get("completed"),
            "notes": request.form.get("notes")
        }
        return redirect("/")

    # If GET, pass the specific log data back to the template to pre-fill the form
    return render_template(
        "index.html",
        activities=activities,
        logs=activity_logs,
        edit_log=activity_logs[log_id],
        edit_id=log_id
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)