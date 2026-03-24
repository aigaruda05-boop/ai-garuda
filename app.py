from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# ================= DATABASE CONNECTION =================

def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

# ================= CREATE TABLE =================

def create_table():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS persons (
        id SERIAL PRIMARY KEY,
        name TEXT,
        age TEXT,
        place TEXT,
        description TEXT,
        image TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

create_table()

# ================= HOME =================

@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM persons ORDER BY id DESC")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", data=data)

# ================= REPORT MISSING =================

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        place = request.form["place"]
        description = request.form["description"]
        image = request.form["image"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO persons (name, age, place, description, image) VALUES (%s, %s, %s, %s, %s)",
            (name, age, place, description, image)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("home"))

    return render_template("report.html")

# ================= SEARCH =================

@app.route("/search", methods=["POST"])
def search():
    keyword = request.form["keyword"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM persons WHERE name ILIKE %s OR place ILIKE %s",
        (f"%{keyword}%", f"%{keyword}%")
    )

    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", data=data)

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
