import sqlite3
import os
from flask import Flask, g, request, render_template, redirect

app = Flask(__name__)

DATABASE = os.path.join(os.getcwd(), 'birthdays.db')

# Database connection management. I didnt write this :p
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        new_name = request.form.get("name")
        new_month = request.form.get("month")
        new_day = request.form.get("day")

        try:
            new_day = int(new_day)
        except ValueError:
            return redirect("/day_error")
        
        if 1 <= new_day <= 31:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO birthdays (name, month, day) VALUES (?, ?, ?)",
                           (new_name, new_month, new_day))
            # Vertical monitor line jump hehe
            conn.commit()
            cursor.close()
            return redirect("/")
        else:
            return redirect("/day_error")

    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM birthdays")
        all_birthdays = cursor.fetchall()
        cursor.close()

        return render_template("index.html", birthday_list=all_birthdays)

@app.route("/delete", methods=["POST"])
def delete():
    deleted_id = request.form.get("id")

    if deleted_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM birthdays WHERE id = ?", (deleted_id,))
        conn.commit()
        cursor.close()
    
    return redirect("/")

@app.route("/day_error", methods=["GET", "POST"])
def error():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("day_error.html")

if __name__ == "__main__":
    app.run(debug=True)
