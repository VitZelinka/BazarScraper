from sys import flags
from flask import Flask, request, render_template, session, redirect, url_for
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from functions import dbSelectCall

app = Flask(__name__)

app.secret_key = b'7s86sd5fsd567fs5678'
app.config['MYSQL_HOST'] = '192.168.0.188'
app.config['MYSQL_USER'] = 'client'
app.config['MYSQL_PASSWORD'] = 'memicko'
app.config['MYSQL_DB'] = 'bazarscraper'

mysql = MySQL(app)

@app.route('/')
@app.route('/home')
def index():
    #print(flask.request.remote_addr)
    user = {'username': 'JGHdkjfhskjf'}
    return render_template("index.html", title="XD", user=user)


@app.route("/authorize", methods=["GET", "POST"])
def auth():
    if "username" in session:
        print(session["username"])
        return "<h1>ALREADY LOGGED IN</h1>"
    if request.method == "POST":
        if "loginForm" in request.form:
            name = request.form["user"]
            passw = request.form["pass"]
            dbresponse = dbSelectCall(mysql, f"SELECT password FROM users WHERE username='{name}';")
            if len(dbresponse) == 1:
                respo = check_password_hash(dbresponse[0][0], passw)
                if respo == True:
                    session["username"] = name
                    return "<h1>LOGGED IN</h1>"
                elif respo == False:
                    return "<h1>WRONG USERNAME OR PASS</h1>"
                else:
                    return "<h1>UNKNOWN ERROR</h1>"
            else:
                return "<h1>WRONG USERNAME OR PASS2</h1>"
        elif "registerForm" in request.form:
            name = request.form["user"]
            passw = request.form["pass"]
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT EXISTS(SELECT * FROM users WHERE username = '{name}');")
            dbresponse = cur.fetchall()
            if dbresponse[0][0] == 0:
                print("Succesfully registered.")
                hashPass = generate_password_hash(passw, method="sha256", salt_length=10)
                cur.execute(f"INSERT INTO users (username, password) VALUES ('{name}', '{hashPass}');")
                mysql.connection.commit()
                cur.close()
            else:
                print("Username already exists.") #unfinished
    return render_template("login.html")


@app.route("/inzerat/<xd>")
def inzerat(xd):
    return xd


@app.route("/browse")
def browse():
    cur = mysql.connection.cursor()
    cur.execute("SELECT heading, imgurl FROM items;")
    dbresponse = cur.fetchall()
    cur.close()
    return render_template("browse.html", items = dbresponse)


@app.route("/profile")
def profile():
    return "profile"


@app.route("/admin")
def admin():
    memexd = "itemid"
    xddd = dbSelectCall(mysql, f"SELECT {memexd} FROM items;")
    print(xddd[0][0])
    return str(xddd[0][0])


@app.route("/test")
def test():
    return render_template("test.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth'))


if __name__ == "__main__":
    app.run(port=5000, debug=False)