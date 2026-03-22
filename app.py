from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os
import time

app = Flask(__name__)
app.secret_key = "aigaruda_secret"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("missing.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS persons(
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
        photo TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------- HOME ----------
@app.route("/")
def home():
    search = request.args.get("search")

    conn = sqlite3.connect("missing.db")
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
        c.execute("SELECT * FROM persons")

    persons = c.fetchall()
    conn.close()

    return render_template("index.html", persons=persons)


# ---------- ADD ----------
@app.route("/add", methods=["GET","POST"])
def add():

    if request.method == "POST":

        # GET DATA
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

        # VALIDATION
        if not all([name, age, state, district, village, colony, date_missing, contact, description]) or not photo:
            flash("Please fill all fields!", "error")
            return redirect("/add")

        # SAVE IMAGE
        filename = str(time.time()) + photo.filename
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        # SAVE DATA
        conn = sqlite3.connect("missing.db")
        c = conn.cursor()

        c.execute("""
        INSERT INTO persons (
            name, age, state, district, village, colony,
            date_missing, contact, description,
            photo, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, age, state, district, village, colony,
            date_missing, contact, description,
            filename, "Missing"
        ))

        conn.commit()
        conn.close()

        flash("Person reported successfully!", "success")
        return redirect("/")

    return render_template("add_person.html")


# ---------- VIEW ----------
@app.route("/person/<int:id>")
def person_details(id):

    conn = sqlite3.connect("missing.db")
    c = conn.cursor()

    c.execute("SELECT * FROM persons WHERE id=?", (id,))
    person = c.fetchone()

    conn.close()

    return render_template("person_details.html", person=person)


# ---------- EDIT ----------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    conn = sqlite3.connect("missing.db")
    c = conn.cursor()

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

        # VALIDATION
        if not all([name, age, state, district, village, colony, date_missing, contact, description]):
            flash("All fields are required!", "error")
            return redirect(f"/edit/{id}")

        c.execute("""
        UPDATE persons SET
        name=?, age=?, state=?, district=?, village=?, colony=?,
        date_missing=?, contact=?, description=?
        WHERE id=?
        """, (
            name, age, state, district, village, colony,
            date_missing, contact, description,
            id
        ))

        conn.commit()
        conn.close()

        flash("Updated successfully!", "success")
        return redirect("/")

    c.execute("SELECT * FROM persons WHERE id=?", (id,))
    person = c.fetchone()

    conn.close()

    return render_template("edit_person.html", person=person)


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)