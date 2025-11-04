from flask import Blueprint, render_template, redirect, url_for, jsonify
import subprocess, sys, os
from datetime import datetime
from src.ticket_manager import fetch_all_tickets

main = Blueprint("main", __name__)

automation_process = None
automation_running = False


@main.route("/")
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


@main.route("/start")
def start():
    global automation_process, automation_running
    if not automation_running:
        script_path = os.path.join(os.getcwd(), "src", "email_reader.py")
        automation_process = subprocess.Popen([sys.executable, script_path])
        automation_running = True
    return redirect(url_for("main.index"))


@main.route("/stop")
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


@main.route("/tickets")
def tickets():
    try:
        all_tickets = fetch_all_tickets()
    except Exception as e:
        print("Error fetching tickets:", e)
        all_tickets = []
    return render_template("tickets.html", tickets=all_tickets)


@main.route("/analysis")
def analysis():
    """Chart view"""
    return render_template("analysis.html")


@main.route("/api/ticket_stats")
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
