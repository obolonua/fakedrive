from flask import Flask
from flask import render_template
import config

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    return render_template("main.html")

@app.route("/signup")
def reegister():
    return  render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")