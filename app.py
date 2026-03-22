from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ================= CONFIG =================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= DATABASE =================
def get_db_connection():
    conn = sqlite3.connect("missing.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= HOME =================
@app.route("/")
def index():
    conn = get_db_connection()
    persons = conn.execute("SELECT * FROM persons").fetchall()
    conn.close()
    return render_template("index.html", persons=persons)


# ================= ADD PERSON =================
@app.route("/add", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        place = request.form.get("place")
        description = request.form.get("description")

        file = request.files.get("image")
        filename = ""

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO persons (name, age, place, description, image) VALUES (?, ?, ?, ?, ?)",
            (name, age, place, description, filename),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_person.html")


# ================= PERSON DETAILS =================
@app.route("/person/<int:id>")
def person_details(id):
    conn = get_db_connection()
    person = conn.execute("SELECT * FROM persons WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template("person_details.html", person=person)


# ================= EDIT PERSON =================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_person(id):
    conn = get_db_connection()
    person = conn.execute("SELECT * FROM persons WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        place = request.form.get("place")
        description = request.form.get("description")

        conn.execute(
            "UPDATE persons SET name=?, age=?, place=?, description=? WHERE id=?",
            (name, age, place, description, id),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_person.html", person=person)


# ================= DELETE PERSON =================
@app.route("/delete/<int:id>")
def delete_person(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM persons WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# ================= SEARCH =================
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")

    conn = get_db_connection()
    persons = conn.execute(
        "SELECT * FROM persons WHERE place LIKE ?", ("%" + query + "%",)
    ).fetchall()
    conn.close()

    return render_template("index.html", persons=persons)


# ================= RUN (IMPORTANT FOR RENDER) =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
