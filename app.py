from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database connection
def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="221203",
        database="authdb",
        cursorclass=pymysql.cursors.DictCursor
    )

login_manager = LoginManager(app)
login_manager.login_view = "login"

# User class
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
    conn.close()

    if user:
        return User(user["id"], user["username"], user["role"])
    return None

@app.route("/")
def home():
    return redirect(url_for("login"))

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
        conn.commit()
        conn.close()

        flash("Registered successfully")
        return redirect(url_for("login"))

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            user_obj = User(user["id"], user["username"], user["role"])
            login_user(user_obj)
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")

# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# Admin Route (Authorization)
@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        return "Access Denied", 403
    return render_template("admin.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
