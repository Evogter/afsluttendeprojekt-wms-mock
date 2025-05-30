from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from models import db, User, Log
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)
app.secret_key = "your_secret_key_here"

BASE_URL = "https://7c7d0cff-5448-4fb5-ab3c-d61af987163f.mock.pstmn.io/api/v1"

@app.route("/", methods=["GET"])
def dashboard():
    token = session.get("token")
    if not token:
        return redirect(url_for("login"))

    devices = get_devices(token)
    query = request.args.get("search", "").lower()

    try:
        selected_id = int(request.args.get("device", 1))
    except ValueError:
        selected_id = 1

    refresh = request.args.get("refresh", "never")
    device_info = get_device(selected_id, token)
    updates = get_updates(token)

    if query:
        updates = [u for u in updates if query in u["deviceName"].lower()]

    return render_template("dashboard.html", devices=devices, device_info=device_info, updates=updates, selected_id=selected_id, refresh=refresh)

@app.route("/stats")
def stats():
    token = session.get("token")
    role = session.get("role")

    if not token:
        return redirect(url_for("login"))

    if role != "admin":
        return redirect(url_for("dashboard"))

    devices = get_devices(token)
    updates = get_updates(token)

    num_online = len([d for d in devices if d["status"] == "online"])
    num_offline = len(devices) - num_online
    updates_available = len([u for u in updates if u["updateAvailable"]])

    return render_template("stats.html", num_online=num_online, num_offline=num_offline, updates_available=updates_available)

@app.route("/logs")
def view_logs():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template("logs.html", logs=logs)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = request.args.get("message")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["token"] = api_login()
            session["role"] = user.role
            session["username"] = user.username

            log = Log(action="Login", user=username)
            db.session.add(log)
            db.session.commit()

            return redirect(url_for("dashboard"))
        else:
            error = "Username or password is incorrect. Try again."

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    message = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if User.query.filter_by(username=username).first():
            message = "User already exists."
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw, role=role)

            db.session.add(new_user)
            db.session.commit()

            log = Log(action=f"Created User: {username}", user=session.get("username"))
            db.session.add(log)
            db.session.commit()

            message = "User created successfully."

    return render_template("create_user.html", message=message)

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    users = User.query.all()
    message = None

    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            message = "⚠️ Passwords do not match."
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                user.password = generate_password_hash(new_password)
                db.session.commit()

                log = Log(action=f"Changed password for: {username}", user=session.get("username", "admin"))
                db.session.add(log)
                db.session.commit()

                message = f"✅ Password changed for user '{username}'."
            else:
                message = "⚠️ User not found."

    return render_template("change_password.html", users=users, message=message)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    message = None

    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not username or not new_password:
            message = "⚠️ All fields are required."
        elif new_password != confirm_password:
            message = "⚠️ Passwords do not match."
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                user.password = generate_password_hash(new_password)
                db.session.commit()

                log = Log(action=f"Reset password for user: {username}", user="anonymous")
                db.session.add(log)
                db.session.commit()

                message = "✅ Password reset successfully. You can now log in."
                return redirect(url_for("login", message=message))

            else:
                message = "⚠️ No such user."

    return render_template("reset_password.html", message=message)

@app.route("/api/device/<int:device_id>")
def api_device(device_id):
    token = session.get("token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    device = get_device(device_id, token)
    return jsonify(device)

def api_login():
    url = f"{BASE_URL}/Auth/Login"
    payload = {"username": "admin", "password": "ApiMock2025"}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def get_devices(token):
    url = f"{BASE_URL}/Devices"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        devices = response.json()
        for d in devices:
            d["lastCheckIn"] = datetime.now().strftime("%d-%m-%Y %H:%M")
        return devices
    return []

def get_device(device_id, token):
    url = f"{BASE_URL}/Devices/{device_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        device = response.json()
        device["lastCheckIn"] = datetime.now().strftime("%d-%m-%Y %H:%M")
        return device
    return {}

def get_updates(token):
    url = f"{BASE_URL}/Updates"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("updates", [])
    return []

@app.route("/api/updates")
def api_updates():
    token = session.get("token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    query = request.args.get("search", "").lower()
    updates = get_updates(token)

    if query:
        updates = [u for u in updates if query in u["deviceName"].lower()]

    return jsonify(updates)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                password=generate_password_hash("ApiMock2025"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)


