from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "crm_secret_key_123"

def get_db():
    conn = sqlite3.connect("crm.db")
    conn.row_factory = sqlite3.Row
    return conn

# check login first
def logged_in():
    return "admin" in session


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        res = cur.fetchone()
        conn.close()
        if res:
            session["admin"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Wrong username or password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    total_clients = cur.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    active_projects = cur.execute("SELECT COUNT(*) FROM projects WHERE status='Ongoing'").fetchone()[0]
    pending_invoices = cur.execute("SELECT COUNT(*) FROM invoices WHERE status='Unpaid'").fetchone()[0]
    conn.close()
    return render_template("dashboard.html", total_clients=total_clients,
                           active_projects=active_projects, pending_invoices=pending_invoices)


@app.route("/clients", methods=["GET", "POST"])
def clients():
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        if not name:
            flash("Client name is required")
        else:
            cur.execute("INSERT INTO clients (name, company, email, phone, city, created_at) VALUES (?,?,?,?,?, date('now'))",
                        (name, request.form["company"], request.form["email"],
                         request.form["phone"], request.form["city"]))
            conn.commit()
            flash("Client added")
        conn.close()
        return redirect(url_for("clients"))

    search = request.args.get("search", "")
    if search:
        cur.execute("SELECT * FROM clients WHERE name LIKE ? ORDER BY id DESC", ("%" + search + "%",))
    else:
        cur.execute("SELECT * FROM clients ORDER BY id DESC")
    all_clients = cur.fetchall()
    conn.close()
    # TODO: add pagination later
    return render_template("clients.html", clients=all_clients, search=search)


@app.route("/clients/edit/<int:id>", methods=["GET", "POST"])
def edit_client(id):
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        if not name:
            flash("Client name is required")
        else:
            cur.execute("UPDATE clients SET name=?, company=?, email=?, phone=?, city=? WHERE id=?",
                        (name, request.form["company"], request.form["email"],
                         request.form["phone"], request.form["city"], id))
            conn.commit()
            conn.close()
            flash("Client updated")
            return redirect(url_for("clients"))
    client = cur.execute("SELECT * FROM clients WHERE id=?", (id,)).fetchone()
    conn.close()
    if not client:
        return redirect(url_for("clients"))
    return render_template("edit_client.html", client=client)


@app.route("/clients/delete/<int:id>")
def delete_client(id):
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    # delete their projects and invoices too so nothing is left hanging
    cur.execute("DELETE FROM invoices WHERE project_id IN (SELECT id FROM projects WHERE client_id=?)", (id,))
    cur.execute("DELETE FROM projects WHERE client_id=?", (id,))
    cur.execute("DELETE FROM clients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Client deleted")
    return redirect(url_for("clients"))


@app.route("/projects", methods=["GET", "POST"])
def projects():
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        if not title:
            flash("Project title is required")
        else:
            cur.execute("INSERT INTO projects (client_id, title, status, start_date, end_date) VALUES (?,?,?,?,?)",
                        (request.form["client_id"], title, request.form["status"],
                         request.form["start_date"], request.form["end_date"]))
            conn.commit()
            flash("Project added")
        conn.close()
        return redirect(url_for("projects"))

    cur.execute("""SELECT projects.*, clients.name as client_name FROM projects
                   JOIN clients ON projects.client_id = clients.id ORDER BY projects.id DESC""")
    all_projects = cur.fetchall()
    client_list = cur.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    conn.close()
    return render_template("projects.html", projects=all_projects, client_list=client_list)


@app.route("/projects/status/<int:id>")
def toggle_project(id):
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    p = cur.execute("SELECT status FROM projects WHERE id=?", (id,)).fetchone()
    if p:
        new_status = "Completed" if p["status"] == "Ongoing" else "Ongoing"
        cur.execute("UPDATE projects SET status=? WHERE id=?", (new_status, id))
        conn.commit()
    conn.close()
    return redirect(url_for("projects"))


@app.route("/invoices", methods=["GET", "POST"])
def invoices():
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        amount = request.form["amount"]
        if not amount:
            flash("Amount is required")
        else:
            cur.execute("INSERT INTO invoices (project_id, amount, status, invoice_date) VALUES (?,?,?, date('now'))",
                        (request.form["project_id"], amount, request.form["status"]))
            conn.commit()
            flash("Invoice created")
        conn.close()
        return redirect(url_for("invoices"))

    cur.execute("""SELECT invoices.*, projects.title as project_title, clients.name as client_name
                   FROM invoices JOIN projects ON invoices.project_id = projects.id
                   JOIN clients ON projects.client_id = clients.id ORDER BY invoices.id DESC""")
    all_invoices = cur.fetchall()
    project_list = cur.execute("SELECT id, title FROM projects ORDER BY title").fetchall()
    conn.close()
    return render_template("invoices.html", invoices=all_invoices, project_list=project_list)


@app.route("/invoices/paid/<int:id>")
def mark_paid(id):
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE invoices SET status='Paid' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("invoices"))


@app.route("/invoices/print/<int:id>")
def print_invoice(id):
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT invoices.*, projects.title as project_title, clients.name as client_name,
                   clients.company, clients.city FROM invoices
                   JOIN projects ON invoices.project_id = projects.id
                   JOIN clients ON projects.client_id = clients.id WHERE invoices.id=?""", (id,))
    inv = cur.fetchone()
    conn.close()
    if not inv:
        return redirect(url_for("invoices"))
    # print(inv["amount"])
    return render_template("invoice_print.html", inv=inv)


@app.route("/reports")
def reports():
    if not logged_in():
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as total
                   FROM clients GROUP BY month ORDER BY month""")
    clients_per_month = cur.fetchall()
    revenue = cur.execute("SELECT SUM(amount) FROM invoices WHERE status='Paid'").fetchone()[0]
    pending = cur.execute("SELECT SUM(amount) FROM invoices WHERE status='Unpaid'").fetchone()[0]
    conn.close()
    return render_template("reports.html", clients_per_month=clients_per_month,
                           revenue=revenue or 0, pending=pending or 0)


if __name__ == "__main__":
    # port 5000 clashes with AirPlay on mac
    app.run(debug=True, port=5001)
