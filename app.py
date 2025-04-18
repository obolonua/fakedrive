import sqlite3
from flask import Flask
from flask import render_template, request
from werkzeug.security import generate_password_hash
import db

app = Flask(__name__)

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