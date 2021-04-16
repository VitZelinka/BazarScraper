from flask import Flask, request, render_template, session, redirect, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
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
                    cur = mysql.connection.cursor()
                    cur.execute(f"INSERT INTO logs (author, message) VALUES ('User {dbresponse[0][1]}', 'Logged in.');")
                    mysql.connection.commit()
                    cur.close()
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
                cur = mysql.connection.cursor()
                cur.execute(f"INSERT INTO logs (author, message) VALUES ('User {dbresponse[0][0]}', 'Registered.');")
                mysql.connection.commit()
                cur.close()
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
                WHERE bazar = '{bazarQuery}' AND public=1 ORDER BY {sortCond} 
                LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, f"""SELECT COUNT(*) FROM items 
                WHERE bazar = '{bazarQuery}' AND public=1;""")
        else:
            dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid, url, bazar FROM items WHERE public=1 
                ORDER BY {sortCond} LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, "SELECT COUNT(*) FROM items WHERE public=1;")
        pageData = ["", pageQuery, dbresponseItemCount[0][0], itemsPerPage,  sortQuery, bazarQuery]
    else:
        searchQuery = searchQuery.replace("'", "")
        if bazarQuery != "any":
            dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid, url, bazar FROM items
                WHERE heading LIKE '%{searchQuery}%' AND bazar = '{bazarQuery}' AND public=1 ORDER BY {sortCond} 
                LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, f"""SELECT COUNT(*) FROM items 
                WHERE heading LIKE '%{searchQuery}%' AND bazar = '{bazarQuery}' AND public=1;""")
        else:
            dbresponseItems = dbSelectCall(mysql, f"""SELECT heading, imgurl, itemid, url, bazar FROM items
                WHERE heading LIKE '%{searchQuery}%'  AND public=1 ORDER BY {sortCond} 
                LIMIT {(pageQuery-1)*itemsPerPage}, {itemsPerPage};""")
            dbresponseItemCount = dbSelectCall(mysql, f"""SELECT COUNT(*) FROM items 
                WHERE heading LIKE '%{searchQuery}%' AND public=1;""")
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
            dbresponseUnpItems = dbSelectCall(mysql, "SELECT itemid FROM items WHERE public = 0;")
            dbresponseUsers = dbSelectCall(mysql, "SELECT userid, username FROM users;")
            dbresponseReports = dbSelectCall(mysql, """SELECT items.heading, items.imgurl, items.itemid, items.url, COUNT(reports.itemid) AS reports 
                FROM items LEFT JOIN reports ON items.itemid = reports.itemid GROUP BY items.itemid HAVING reports > 0 ORDER BY reports DESC;""")
            dbresponseAdmins = dbSelectCall(mysql, "SELECT userid FROM administrators;")
            dbresponseLogs = dbSelectCall(mysql, "SELECT logid, author, message, datecreated FROM logs ORDER BY datecreated DESC;")
            unpItems = []
            for i in dbresponseUnpItems:
                unpItems.append(i[0])
            admins = []
            for i in dbresponseAdmins:
                admins.append(i[0])
            return render_template("admin.html", items=dbresponseItems, unpItems=unpItems,
                users=dbresponseUsers, reports=dbresponseReports, admins=admins, logs=dbresponseLogs)
        else:
            abort(404)
    else:
        abort(404)

#-----------------------------END POINTS-----------------------------#

@app.route("/addfav", methods=["POST"])
def addFav():
    if "username" in session:
        userId = session["userId"]
        itemId = request.form["itemId"]
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO favourites (userId, itemId) VALUES ('{userId}', '{itemId}');")
        cur.execute(f"INSERT INTO logs (author, message) VALUES ('User {userId}', 'Added item {itemId} to favourites.');")
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
        cur.execute(f"INSERT INTO logs (author, message) VALUES ('User {userId}', 'Removed item {itemId} from favourites.');")
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
        cur.execute(f"INSERT INTO logs (author, message) VALUES ('User {userId}', 'Reported item {itemId}.');")
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
            cur.execute(f"INSERT INTO logs (author, message) VALUES ('Admin {userId}', 'Unpublished item {itemId}.');")
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
            cur.execute(f"INSERT INTO logs (author, message) VALUES ('Admin {userId}', 'Published item {itemId}.');")
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
            cur.execute(f"INSERT INTO logs (author, message) VALUES ('Admin {userId}', 'Deleted item {itemId}.');")
            mysql.connection.commit()
            cur.close()
            return ""
        else:
            abort(404)
    else:
        abort(404)


@app.route("/deleteuser", methods=["POST"])
def deleteuser():
    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT EXISTS(SELECT * FROM administrators WHERE userId = %s);", [userId])[0][0]
        if dbresponse == 1:
            userIdToDel = request.form["userId"]
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM users WHERE userid = %s;", [userIdToDel])
            cur.execute("DELETE FROM favourites WHERE userid = %s;", [userIdToDel])
            cur.execute("DELETE FROM administrators WHERE userid = %s;", [userIdToDel])
            cur.execute(f"INSERT INTO logs (author, message) VALUES ('Admin {userId}', 'Deleted user {userIdToDel}.');")
            mysql.connection.commit()
            cur.close()
            return ""
        else:
            abort(404)
    else:
        abort(404)


@app.route("/grant", methods=["POST"])
def grant():
    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT EXISTS(SELECT * FROM administrators WHERE userId = %s);", [userId])[0][0]
        if dbresponse == 1:
            userIdToGrant = request.form["userId"]
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO administrators (userid) VALUES (%s);", [userIdToGrant])
            cur.execute(f"INSERT INTO logs (author, message) VALUES ('Admin {userId}', 'Granted administrator to user {userIdToGrant}.');")
            mysql.connection.commit()
            cur.close()
            return ""
        else:
            abort(404)
    else:
        abort(404)


@app.route("/revoke", methods=["POST"])
def revoke():
    if "username" in session:
        userId = session["userId"]
        dbresponse = dbSelectCallEsc(mysql, "SELECT EXISTS(SELECT * FROM administrators WHERE userId = %s);", [userId])[0][0]
        if dbresponse == 1:
            userIdToRevoke = request.form["userId"]
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM administrators WHERE userid = %s;", [userIdToRevoke])
            cur.execute(f"INSERT INTO logs (author, message) VALUES ('Admin {userId}', 'Revoked administrator from user {userIdToRevoke}.');")
            mysql.connection.commit()
            cur.close()
            return ""
        else:
            abort(404)
    else:
        abort(404)


@app.route("/logout")
def logout():
    userId = session["userId"]
    session.pop('username', None)
    session.pop('userId', None)
    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO logs (author, message) VALUES ('User {userId}', 'Logged off.');")
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)