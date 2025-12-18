import os
from datetime import datetime
import pytz

from flask import Flask, request, session, redirect, render_template_string, jsonify


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError("Admin credentials not set in environment variables")


app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_123"   # change later



# ---------------- DATA ----------------
company_status = {
    "SMARTGRID_INNOVATION": "blocked",
    "BHARTECHSMART_INDUSTRIAL": "blocked",
    "SHETE_ADVANCE": "blocked"
}

connected_pcs = {}

# ---------------- HTML TEMPLATES ----------------

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Admin Login</title>
<style>
body { font-family: Arial; background:#f4f6f8; }
.box { width:300px; margin:120px auto; padding:20px; background:white; box-shadow:0 0 10px #ccc; }
button { width:100%; padding:10px; background:#007bff; color:white; border:none; }
</style>
</head>
<body>
<div class="box">
<h2>Admin Login</h2>
<form method="post">
<input name="user" placeholder="Username" required><br><br>
<input name="pass" type="password" placeholder="Password" required><br><br>
<button>Login</button>
</form>
<p style="color:red">{{ error }}</p>
</div>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Control Dashboard</title>
<style>
body { font-family: Arial; background:#eef2f5; }
.container { width:90%; margin:auto; }
.card { background:white; padding:15px; margin:10px 0; box-shadow:0 0 8px #ccc; }
button { padding:6px 12px; margin:5px; border:none; cursor:pointer; }
.allow { background:#28a745; color:white; }
.block { background:#dc3545; color:white; }
.logout { float:right; background:#000; color:white; }
table { width:100%; border-collapse:collapse; }
th,td { border:1px solid #ccc; padding:8px; text-align:center; }
</style>
</head>

<body>
<div class="container">
<h2>Admin Control Panel
<a href="/logout"><button class="logout">Logout</button></a>
</h2>

<h3>Company Control</h3>
{% for c,s in companies.items() %}
<div class="card">
<b>{{ c }}</b> — Status: <b>{{ s }}</b><br>
<a href="/admin/allow/{{ c }}"><button class="allow">ALLOW</button></a>
<a href="/admin/block/{{ c }}"><button class="block">BLOCK</button></a>
</div>
{% endfor %}

<h3>Live Connected PCs</h3>
<table>
<tr><th>PC ID</th><th>Company</th><th>Last Seen</th></tr>
{% for pc,info in pcs.items() %}
<tr>
<td>{{ pc }}</td>
<td>{{ info.company }}</td>
<td>{{ info.last_seen }}</td>
</tr>
{% endfor %}
</table>
</div>
</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect("/admin")

    if request.method == "POST":
        if request.form["user"] == ADMIN_USER and request.form["pass"] == ADMIN_PASS:
            session["logged_in"] = True
            return redirect("/admin")
        return render_template_string(LOGIN_HTML, error="Wrong login")

    return render_template_string(LOGIN_HTML, error="")

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect("/")
    return render_template_string(ADMIN_HTML, companies=company_status, pcs=connected_pcs)

@app.route("/admin/allow/<company>")
def allow(company):
    if not session.get("logged_in"):
        return redirect("/")
    company_status[company] = "allowed"
    return redirect("/admin")

@app.route("/admin/block/<company>")
def block(company):
    if not session.get("logged_in"):
        return redirect("/")
    company_status[company] = "blocked"
    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- CLIENT CHECK ----------------
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    tz = pytz.timezone("Asia/Kolkata")  # change to your timezone
    now = datetime.now(tz)
    
    connected_pcs[data["pc_id"]] = {
        "company": data["company_id"],
        "last_seen": now.strftime("%d-%m-%y %H:%M:%S")
    }
    return jsonify({
        "status": company_status.get(data["company_id"], "blocked")
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
