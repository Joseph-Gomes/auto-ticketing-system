from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, flash
import subprocess, sys, os
from datetime import datetime
from src.ticket_manager import fetch_all_tickets
from werkzeug.security import check_password_hash, generate_password_hash
import os

main = Blueprint("main", __name__)

# ------------------------------
# 🔒 Login Configuration
# ------------------------------
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS_HASH = os.getenv(
    "ADMIN_PASS_HASH",
    generate_password_hash(os.getenv("ADMIN_PASS", "password123"))
)

# ------------------------------
# 🧠 App State
# ------------------------------
automation_process = None
automation_running = False


# ------------------------------
# 🧱 Helper: Login required decorator
# ------------------------------
def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("main.login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ------------------------------
# 🔑 Login Routes
# ------------------------------
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and check_password_hash(ADMIN_PASS_HASH, password):
            session["logged_in"] = True
            flash("Login successful!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")


@main.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


# ------------------------------
# 🏠 Dashboard (Protected)
# ------------------------------
@main.route("/")
@login_required
def index():
    """Home + Dashboard combined"""
    global automation_running
    status = "🟢 Running" if automation_running else "🔴 Stopped"

    # Fetch ticket data
    tickets = []
    try:
        tickets = fetch_all_tickets()
    except Exception as e:
        print("Error fetching tickets:", e)

    # Count tickets (daily summary)
    today = datetime.now().strftime("%Y-%m-%d")
    today_tickets = [t for t in tickets if t.get("timestamp", "").startswith(today)]
    open_tickets = [t for t in today_tickets if t.get("status", "").lower() == "open"]
    closed_tickets = [t for t in today_tickets if t.get("status", "").lower() == "closed"]

    daily_summary = {
        "total": len(today_tickets),
        "open": len(open_tickets),
        "closed": len(closed_tickets),
    }

    return render_template("index.html", status=status, summary=daily_summary)


# ------------------------------
# ▶ Start / Stop Automation (Protected)
# ------------------------------
@main.route("/start")
@login_required
def start():
    global automation_process, automation_running
    if not automation_running:
        script_path = os.path.join(os.getcwd(), "src", "email_reader.py")
        automation_process = subprocess.Popen([sys.executable, script_path])
        automation_running = True
    return redirect(url_for("main.index"))


@main.route("/stop")
@login_required
def stop():
    global automation_process, automation_running
    if automation_running and automation_process:
        try:
            automation_process.terminate()
        except Exception:
            pass
        automation_running = False
        automation_process = None
    return redirect(url_for("main.index"))


# ------------------------------
# 🎟 Tickets Page (Protected)
# ------------------------------
@main.route("/tickets")
@login_required
def tickets():
    try:
        all_tickets = fetch_all_tickets()
    except Exception as e:
        print("Error fetching tickets:", e)
        all_tickets = []
    return render_template("tickets.html", tickets=all_tickets)


# ------------------------------
# 📊 Analysis / Charts (Protected)
# ------------------------------
@main.route("/analysis")
@login_required
def analysis():
    """Chart view"""
    return render_template("analysis.html")


@main.route("/api/ticket_stats")
@login_required
def api_ticket_stats():
    """Provide data for Chart.js"""
    try:
        tickets = fetch_all_tickets()
    except Exception as e:
        print("Error fetching tickets:", e)
        return jsonify([])

    counts = {}
    for t in tickets:
        ts = t.get("timestamp")
        if not ts:
            continue
        date = ts.split(" ")[0]
        counts[date] = counts.get(date, 0) + 1

    items = sorted(counts.items(), key=lambda x: x[0])
    return jsonify(items)
