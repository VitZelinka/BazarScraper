from sys import flags
from flask import Flask, request, render_template, session, redirect, url_for, abort
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from werkzeug.utils import escape
from functions import dbSelectCall, dbSelectCallEsc

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
            dbresponse = dbSelectCallEsc(mysql, "SELECT password, userid, username FROM users WHERE username=%s;", [name])
            if len(dbresponse) == 1:
                respo = check_password_hash(dbresponse[0][0], passw)
                if respo == True:
                    session["username"] = dbresponse[0][2]
                    session["userId"] = dbresponse[0][1]
                    return redirect(url_for('profile'))
                else:
                    return render_template("login.html", authResult="BadLogin")
            else:
                return render_template("login.html", authResult="BadLogin")
        elif "registerForm" in request.form:
            name = request.form["user"]
            passw = request.form["pass"]
            if len(name) < 4:
                return render_template("login.html", authResult="UsernameTooShort")
            if len(passw) < 5:
                return render_template("login.html", authResult="PassTooShort")
            cur = mysql.connection.cursor()
            cur.execute("SELECT EXISTS(SELECT * FROM users WHERE username = %s);", [name])
            dbresponse = cur.fetchall()
            if dbresponse[0][0] == 0:
                hashPass = generate_password_hash(passw, method="sha256", salt_length=10)
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", [name, hashPass])
                mysql.connection.commit()
                cur.close()
                dbresponse = dbSelectCallEsc(mysql, "SELECT userid, username FROM users WHERE username=%s;", [name])
                session["username"] = dbresponse[0][1]
                session["userId"] = dbresponse[0][0]
                return redirect(url_for('profile'))
            else:
                return render_template("login.html", authResult="UsernameExists")
    return render_template("login.html")


@app.route("/browse")
def browse():
    searchQuery = request.args.get("search")
    pageQuery = request.args.get("page")
    sortQuery = request.args.get("sort")
    bazarQuery = request.args.get("bazar")
    itemsPerPage = 15

    try:
        pageQuery = int(pageQuery)
        if pageQuery < 1:
            pageQuery = 1
    except:
        pageQuery = 1

    if sortQuery == "newest" or sortQuery == "" or sortQuery == None:
        sortCond = "dateadded DESC"
    elif sortQuery == "oldest":
        sortCond = "dateadded ASC"
    elif sortQuery == "alphasc":
        sortCond = "heading ASC"
    else:
        sortCond = "heading DESC"
    
    if bazarQuery is None:
        bazarQuery = "any"

    if searchQuery == None or searchQuery == "":
        if bazarQuery != "any":
            dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid, url, bazar FROM items 
                WHERE bazar = '{bazarQuery}' ORDER BY {sortCond} 
                LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, f"""SELECT COUNT(*) FROM items 
                WHERE bazar = '{bazarQuery}';""")
        else:
            dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid, url, bazar FROM items 
                ORDER BY {sortCond} LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, "SELECT COUNT(*) FROM items;")
        pageData = ["", pageQuery, dbresponseItemCount[0][0], itemsPerPage,  sortQuery, bazarQuery]
    else:
        searchQuery = searchQuery.replace("'", "")
        if bazarQuery != "any":
            dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid, url, bazar FROM items
                WHERE heading LIKE '%{searchQuery}%' AND bazar = '{bazarQuery}' ORDER BY {sortCond} 
                LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, f"""SELECT COUNT(*) FROM items 
                WHERE heading LIKE '%{searchQuery}%' AND bazar = '{bazarQuery}';""")
        else:
            dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid, url, bazar FROM items
                WHERE heading LIKE '%{searchQuery}%' ORDER BY {sortCond} 
                LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, f"""SELECT COUNT(*) FROM items 
                WHERE heading LIKE '%{searchQuery}%';""")
        pageData = [searchQuery, pageQuery, dbresponseItemCount[0][0], itemsPerPage, sortQuery, bazarQuery]

    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT itemid FROM favourites WHERE userid = %s", [userId])
        favItems = []
        for i in dbresponse:
            favItems.append(i[0])
        return render_template("browse.html", items=dbresponseItems, loggedIn=True, favItems=favItems, pageData=pageData)
    else:
        return render_template("browse.html", items=dbresponseItems, loggedIn=False, pageData=pageData)


@app.route("/profile")
def profile():
    if "username" in session:
        username = session["username"]
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, """SELECT items.heading, items.imgurl, items.itemid, items.url, items.bazar 
            FROM items INNER JOIN favourites ON items.itemid=favourites.itemid WHERE userid=%s;""", [userId])
        return render_template("profile.html", items=dbresponse, username=username, loggedIn=True)
    return redirect(url_for('auth'))


#-----------------------------SIDE ROUTES-----------------------------#

@app.route("/admin")
def admin():
    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT EXISTS(SELECT * FROM administrators WHERE userId = %s);", [userId])[0][0]
        if dbresponse == 1:
            dbresponseItems = dbSelectCall(mysql, "SELECT heading, imgurl, itemid, url, bazar, dateadded FROM items ORDER BY dateadded DESC;")
            dbresponseUnpItems = dbSelectCall(mysql, "SELECT itemid FROM items WHERE public = 0")
            dbresponseUsers = dbSelectCall(mysql, "SELECT userid, username FROM users;")
            return render_template("admin.html", items=dbresponseItems, unpItems=dbresponseUnpItems, users=dbresponseUsers)
        else:
            abort(404)
    else:
        abort(404)


@app.route("/addfav", methods=["POST"])
def addFav():
    if "username" in session:
        userId = session["userId"]
        itemId = request.form["itemId"]
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO favourites (userId, itemId) VALUES ('{userId}', '{itemId}');")
        mysql.connection.commit()
        cur.close()
        return ""
    else:
        abort(404)


@app.route("/remfav", methods=["POST"])
def remFav():
    if "username" in session:
        userId = session["userId"]
        itemId = request.form["itemId"]
        cur = mysql.connection.cursor()
        cur.execute(f"DELETE FROM favourites WHERE userid = {userId} AND itemid = {itemId};")
        mysql.connection.commit()
        cur.close()
        return ""
    else:
        abort(404)


@app.route("/report", methods=["POST"])
def report():
    if "username" in session:
        userId = session["userId"]
        itemId = request.form["itemId"]
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO reports (userId, itemId) VALUES ('{userId}', '{itemId}');")
        mysql.connection.commit()
        cur.close()
        return ""
    else:
        abort(404)


@app.route("/unpublish", methods=["POST"])
def unpublish():
    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT EXISTS(SELECT * FROM administrators WHERE userId = %s);", [userId])[0][0]
        if dbresponse == 1:
            itemId = request.form["itemId"]
            cur = mysql.connection.cursor()
            cur.execute("UPDATE items SET public = 0 WHERE itemid = %s;", [itemId])
            mysql.connection.commit()
            cur.close()
            return ""
        else:
            abort(404)
    else:
        abort(404)


@app.route("/publish", methods=["POST"])
def publish():
    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT EXISTS(SELECT * FROM administrators WHERE userId = %s);", [userId])[0][0]
        if dbresponse == 1:
            itemId = request.form["itemId"]
            cur = mysql.connection.cursor()
            cur.execute("UPDATE items SET public = 1 WHERE itemid = %s;", [itemId])
            mysql.connection.commit()
            cur.close()
            return ""
        else:
            abort(404)
    else:
        abort(404)


@app.route("/deleteitem", methods=["POST"])
def deleteitem():
    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT EXISTS(SELECT * FROM administrators WHERE userId = %s);", [userId])[0][0]
        if dbresponse == 1:
            itemId = request.form["itemId"]
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM items WHERE itemid = %s;", [itemId])
            cur.execute("DELETE FROM favourites WHERE itemid = %s;", [itemId])
            cur.execute("DELETE FROM reports WHERE itemid = %s;", [itemId])
            mysql.connection.commit()
            cur.close()
            return ""
        else:
            abort(404)
    else:
        abort(404)


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('userId', None)
    return redirect(url_for('index'))


@app.route("/test")
def test():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)