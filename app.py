from flask import Flask, render_template, request, redirect
import sqlite3
import os
import time

app = Flask(_name_)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DATABASE =================
def get_db():
    return sqlite3.connect("missing.db")


# ================= CREATE TABLE =================
def create_table():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        state TEXT,
        district TEXT,
        village TEXT,
        colony TEXT,
        date_missing TEXT,
        contact TEXT,
        description TEXT,
        photo TEXT
    )
    """)

    conn.commit()
    conn.close()

create_table()


# ================= HOME =================
@app.route("/")
def home():
    search = request.args.get("search")

    conn = get_db()
    c = conn.cursor()

    if search:
        c.execute("""
        SELECT * FROM persons 
        WHERE name LIKE ? 
        OR state LIKE ? 
        OR district LIKE ? 
        OR village LIKE ?
        """, (
            '%' + search + '%',
            '%' + search + '%',
            '%' + search + '%',
            '%' + search + '%'
        ))
    else:
        c.execute("SELECT * FROM persons ORDER BY id DESC")

    persons = c.fetchall()
    conn.close()

    return render_template("index.html", persons=persons)


# ================= ADD =================
@app.route("/add", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":

        name = request.form.get("name")
        age = request.form.get("age")
        state = request.form.get("state")
        district = request.form.get("district")
        village = request.form.get("village")
        colony = request.form.get("colony")
        date_missing = request.form.get("date_missing")
        contact = request.form.get("contact")
        description = request.form.get("description")

        photo = request.files.get("photo")
        filename = ""

        if photo:
            filename = str(time.time()) + photo.filename
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = get_db()
        c = conn.cursor()

        c.execute("""
        INSERT INTO persons (
            name, age, state, district, village, colony,
            date_missing, contact, description, photo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, age, state, district, village, colony,
            date_missing, contact, description, filename
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_person.html")


# ================= DETAILS =================
@app.route("/person/<int:id>")
def person_details(id):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM persons WHERE id=?", (id,))
    person = c.fetchone()

    conn.close()

    return render_template("person_details.html", person=person)


# ================= RUN =================
if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000)
