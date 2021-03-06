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

@app.route("/")
@app.route("/home")
def index():
    #print(flask.request.remote_addr)
    if "username" in session:
        return render_template("index.html", loggedIn=True)
    else:
        return render_template("index.html", loggedIn=False)


@app.route("/authorize", methods=["GET", "POST"])
def auth():
    if "username" in session:
        return redirect(url_for('profile'))
    if request.method == "POST":
        if "loginForm" in request.form:
            name = request.form["user"]
            passw = request.form["pass"]
            dbresponse = dbSelectCall(mysql, f"SELECT password, userid, username FROM users WHERE username='{name}';")
            if len(dbresponse) == 1:
                respo = check_password_hash(dbresponse[0][0], passw)
                if respo == True:
                    session["username"] = dbresponse[0][2]
                    session["userId"] = dbresponse[0][1]
                    print(session["userId"])
                    return redirect(url_for('profile'))
                else:
                    return render_template("login.html", authFailed=True)
            else:
                return render_template("login.html", authFailed=True)
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
                session["username"] = name
                return redirect(url_for('profile'))
            else:
                print("Username already exists.") #unfinished
    return render_template("login.html")


@app.route('/data')
def data():
    # here we want to get the value of user (i.e. ?user=some-value)
    user = request.args.get('user')


@app.route("/browse")
def browse():
    searchQuery = request.args.get("search")
    if searchQuery == None or searchQuery == " ":
        dbresponse = dbSelectCall(mysql, "SELECT heading, imgurl, itemid FROM items;")
    else:
        dbresponse = dbSelectCall(mysql, f"SELECT heading, imgurl, itemid FROM items WHERE heading LIKE '%{searchQuery}%';")
    if "username" in session:
        return render_template("browse.html", items=dbresponse, loggedIn=True)
    else:
        return render_template("browse.html", items=dbresponse, loggedIn=False)


@app.route("/profile")
def profile():
    return render_template("profile.html", username = session["username"])


#-----------------------------SIDE ROUTES-----------------------------#

@app.route("/admin")
def admin():
    memexd = "itemid"
    xddd = dbSelectCall(mysql, f"SELECT {memexd} FROM items;")
    print(xddd[0][0])
    return str(xddd[0][0])


@app.route("/addfav", methods=["POST"])
def addFav():
    print(session["userId"])
    print(request.form["itemId"])
    
    return ""


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)