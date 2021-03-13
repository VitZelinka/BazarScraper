from sys import flags
from flask import Flask, request, render_template, session, redirect, url_for, abort
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


@app.route("/browse")
def browse():
    searchQuery = request.args.get("search")
    pageQuery = request.args.get("page")
    itemsPerPage = 3

    try:
        pageQuery = int(pageQuery)
        if pageQuery < 1:
            pageQuery = 1
    except:
        pageQuery = 1

    if searchQuery == None or searchQuery == " ":
        dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid FROM items 
            LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
        pageData = ["", pageQuery]
    else:
        dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid FROM items
            WHERE heading LIKE '%{searchQuery}%' LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
        pageData = [searchQuery, pageQuery]

    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCall(mysql, f"SELECT itemid FROM favourites WHERE userid = {userId}")
        favItems = []
        for i in dbresponse:
            favItems.append(i[0])
        print(favItems)
        return render_template("browse.html", items=dbresponseItems, loggedIn=True, favItems=favItems, pageData=pageData)
    else:
        return render_template("browse.html", items=dbresponseItems, loggedIn=False, pageData=pageData)


@app.route("/profile")
def profile():
    return render_template("profile.html", username = session["username"])


#-----------------------------SIDE ROUTES-----------------------------#

@app.route("/admin")
def admin():
    if "username" in session and session["username"] == "admin":
        return "admin"
    else:
        abort(404)


@app.route("/addfav", methods=["POST"])
def addFav():
    userId = session["userId"]
    itemId = request.form["itemId"]
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO favourites (userId, itemId) VALUES ('{userId}', '{itemId}');")
    mysql.connection.commit()
    cur.close()
    return ""


@app.route("/remfav", methods=["POST"])
def remFav():
    userId = session["userId"]
    itemId = request.form["itemId"]
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE FROM favourites WHERE userid = {userId} AND itemid = {itemId};")
    mysql.connection.commit()
    cur.close()
    return ""


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('userId', None)
    return redirect(url_for('index'))


@app.route("/test")
def test():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)