import sqlite3
from flask import Flask
from flask import render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/signup")
def signup():
    return  render_template("signup.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password"]
    password2 = request.form["confirm_password"]
    if password1 != password2:
        return "ERROR passwords dont match"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "username already exists"

    return "User registered"

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authentication", methods =["POST"])
def authentication():
    username = request.form["username"]
    password = request.form["password"]
    
    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/My Fakedrive")
    else:
        return "ERROR: wrong username or password"