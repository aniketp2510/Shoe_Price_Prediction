from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = "database.db"

# -------------------------
# DATABASE
# -------------------------
def connect_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gender TEXT,
            size TEXT,
            model TEXT,
            color TEXT,
            brand TEXT,
            type TEXT,
            material TEXT,
            usd REAL,
            inr REAL,
            created TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------------------------------------
# ROUTES
# -----------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def predict():
    price = None
    price_inr = None

    if request.method == "POST":
        brand = request.form["brand"]
        type_ = request.form["type"]
        size = request.form["size"]

        price = round(len(brand) * 5 + len(type_) * 3 + float(size) * 2, 2)
        price_inr = round(price * 84.2, 2)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO predictions 
            (gender, size, model, color, brand, type, material, usd, inr, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form.get("gender"),
            size,
            request.form.get("model"),
            request.form.get("color"),
            brand,
            type_,
            request.form.get("material"),
            price,
            price_inr,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

    return render_template("index.html", price=price, price_inr=price_inr)


# -------------------------
# DASHBOARD (login required)
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cur.fetchone()[0]

    cur.execute("SELECT MAX(usd) FROM predictions")
    highest_price = cur.fetchone()[0] or 0

    cur.execute("SELECT MIN(usd) FROM predictions")
    lowest_price = cur.fetchone()[0] or 0

    cur.execute("SELECT AVG(usd) FROM predictions")
    avg_price = round(cur.fetchone()[0] or 0, 2)

    cur.execute("SELECT model, usd, inr, created FROM predictions ORDER BY id DESC LIMIT 1")
    latest = cur.fetchone()

    conn.close()

    return render_template("dashboard.html",
                           total_predictions=total_predictions,
                           highest_price=highest_price,
                           lowest_price=lowest_price,
                           avg_price=avg_price,
                           latest=latest)


# -------------------------
# HISTORY (login required)
# -------------------------
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM predictions ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return render_template("history.html", history=data)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("history"))


@app.route("/delete_all", methods=["POST"])
def delete_all():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()
    return redirect(url_for("history"))


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid email or password."

    return render_template("login.html", error=error)


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        cpass = request.form["confirm_password"]

        if password != cpass:
            error = "Passwords do not match."
        else:
            try:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                            (name, email, password))
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except:
                error = "Email already exists."

    return render_template("register.html", error=error)


# -------------------------
# START APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
