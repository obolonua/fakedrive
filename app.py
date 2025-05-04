import sqlite3
from flask import Flask
from flask import render_template, request, session, redirect, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import db
import config
import os

app = Flask(__name__)
app.secret_key = config.secret_key
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok = True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/about")
def home():
    return render_template("about.html")

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
    result = db.query(sql, [username])
    if not result:
        return "ERROR: wrong username or password"
    password_hash = result[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/my_fakedrive")
    
@app.route("/my_fakedrive")    
def my_fakedrive():
    if "username" not in session:
        return redirect("/login")
    
    search_query = request.args.get("q", "").strip()

    if search_query:
        sql = """
            SELECT files.id, files.filename, users.username 
            FROM files 
            JOIN users ON files.owner_id = users.id 
            WHERE files.public = 1 AND files.filename LIKE ?
        """
        files = db.query(sql, [f"%{search_query}%"])

    else:
        sql_files = """
            SELECT files.id, files.filename, users.username
            FROM files
            JOIN users ON files.owner_id = users.id
            WHERE files.public = 1
        """
        files = db.query(sql_files)

    return render_template("my_fakedrive.html", files=files, view="all")

@app.route("/my_files")
def my_files():
    if "username" not in session:
        return redirect("/login")
    
    username = session["username"]
    sql_user = "SELECT id FROM users WHERE username = ?"
    user = db.query(sql_user, [username])

    user_id = user[0][0] 
    sql = """
        SELECT files.id, files.filename, users.username
        FROM files
        JOIN users ON files.owner_id = users.id
        WHERE files.owner_id = ? AND files.public = 0
    """
    files = db.query(sql, [user_id])
    return render_template("my_fakedrive.html", files=files, view="my")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "username" not in session:
        return redirect("/login")
    
    file = request.files["file"]
    if file.filename == "":
        return "No file selected"
    
    visibility = request.form.get("visibility", "private")
    is_public = 1 if visibility == "public" else 0

    filename = secure_filename(file.filename)
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], session["username"])
    os.makedirs(user_folder, exist_ok=True)

    path = os.path.join(user_folder, filename)
    file.save(path)

    sql = """
    INSERT INTO files (filename, filepath, owner_id, public)
    VALUES (?, ?, (SELECT id FROM users WHERE username = ?), ?)
    """
    db.execute(sql, [filename, path, session["username"], is_public])
    
    return redirect("/my_fakedrive")

@app.route("/download/<int:file_id>")
def download(file_id):
    if "username" not in session:
        return redirect("/login")

    sql = "SELECT filepath FROM files WHERE id = ?"
    result = db.query(sql, [file_id])
    
    if not result:
        return "File not found"

    filepath = result[0][0]
    return send_file(filepath, as_attachment=True)

@app.route("/delete/<int:file_id>")
def delete(file_id):
    if "username" not in session:
        return redirect("/login")

    sql = """
    SELECT files.filepath, users.username 
    FROM files 
    JOIN users ON files.owner_id = users.id 
    WHERE files.id = ?
    """
    result = db.query(sql, [file_id])
    if not result:
        return "File not found"

    filepath, owner_username = result[0]

    if session["username"] != owner_username:
        return "Unauthorized", 403

    if os.path.exists(filepath):
        os.remove(filepath)

    db.execute("DELETE FROM files WHERE id = ?", [file_id])

    return redirect("/my_fakedrive")

@app.route("/file/<int:file_id>")
def file_detail(file_id):

    sql_file = "SELECT id, filename, owner_id FROM files WHERE id = ? AND public = 1"
    file = db.query(sql_file, [file_id])
    if not file:
        return "File not found or not public", 404

    file = file[0]

    sql_comments = "SELECT username, message FROM comments WHERE file_id = ? ORDER BY id DESC"
    comments = db.query(sql_comments, [file_id])

    return render_template("file_detail.html", file=file, comments=comments)

@app.route("/file/<int:file_id>/comment", methods=["POST"])
def post_comment(file_id):
    if "username" not in session:
        return redirect("/login")

    message = request.form["message"]
    username = session["username"]

    sql = "INSERT INTO comments (file_id, username, message) VALUES (?, ?, ?)"
    db.execute(sql, [file_id, username, message])

    return redirect(f"/file/{file_id}")