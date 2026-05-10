import os
import requests
from flask import Flask, request, redirect, url_for, render_template_string

API_URL = os.getenv("API_URL", "http://api:8080")
TIMEOUT = 5

app = Flask(__name__)

PAGE = """<!DOCTYPE html>
<html>
<head><title>Nodes Registry Dashboard</title></head>
<body>
<h1>Nodes Registry Dashboard</h1>
<p>This dashboard lists all registered nodes from the API.</p>
<p>API status: {{ status }}</p>
<p>Active nodes count: {{ count }}</p>

<h2>Registered Nodes</h2>
{% if nodes %}
<table border="1">
<thead><tr><th>name</th><th>host</th><th>port</th><th>status</th></tr></thead>
<tbody>
{% for n in nodes %}
<tr>
<td>{{ n.name }}</td>
<td>{{ n.host }}</td>
<td>{{ n.port }}</td>
<td>{{ n.status }}</td>
</tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p>No nodes registered yet.</p>
{% endif %}

<h2>Register a new node</h2>
<form method="post" action="/register">
<label>name: <input name="name"/></label>
<label>host: <input name="host"/></label>
<label>port: <input name="port" type="number" value="8080"/></label>
<button type="submit">Register</button>
</form>

<h2>Delete a node</h2>
<form method="post" action="/delete">
<label>name: <input name="name"/></label>
<button type="submit">Delete</button>
</form>

{% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
"""


def fetch_state():
    status = "unknown"
    count = 0
    nodes = []
    try:
        h = requests.get(f"{API_URL}/health", timeout=TIMEOUT).json()
        status = h.get("status", "unknown")
        count = h.get("nodes_count", 0)
    except requests.RequestException:
        pass
    try:
        nodes = requests.get(f"{API_URL}/api/nodes", timeout=TIMEOUT).json()
    except requests.RequestException:
        nodes = []
    return status, count, nodes


@app.route("/")
def index():
    status, count, nodes = fetch_state()
    msg = request.args.get("msg", "")
    return render_template_string(PAGE, status=status, count=count, nodes=nodes, message=msg)


@app.post("/register")
def register():
    name = request.form.get("name", "").strip()
    host = request.form.get("host", "").strip()
    port = request.form.get("port", "").strip()
    if not name or not host or not port:
        return redirect(url_for("index", msg="name, host, port required"))
    try:
        r = requests.post(
            f"{API_URL}/api/nodes",
            json={"name": name, "host": host, "port": int(port)},
            timeout=TIMEOUT,
        )
        msg = f"registered {name}" if r.status_code in (200, 201) else f"error {r.status_code}"
    except requests.RequestException as e:
        msg = f"error: {e}"
    return redirect(url_for("index", msg=msg))


@app.post("/delete")
def delete():
    name = request.form.get("name", "").strip()
    if not name:
        return redirect(url_for("index", msg="name required"))
    try:
        r = requests.delete(f"{API_URL}/api/nodes/{name}", timeout=TIMEOUT)
        msg = f"deleted {name}" if r.status_code in (200, 204) else f"error {r.status_code}"
    except requests.RequestException as e:
        msg = f"error: {e}"
    return redirect(url_for("index", msg=msg))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501)