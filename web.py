from flask import Flask, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

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
    user = {'username': 'Kokt'}
    return render_template("index.html", title="XD", user=user)


@app.route("/login", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        if "loginForm" in request.form:
            name = request.form["user"]
            passw = request.form["pass"]
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT password FROM users WHERE username='{name}';")
            dbresponse = cur.fetchall()
            cur.close()
            pass_from_db = dbresponse[0][0]
            respo = check_password_hash(pass_from_db, passw)
            print(respo)
        elif "registerForm" in request.form:
            name = request.form["user"]
            passw = request.form["pass"]
            cur = mysql.connection.cursor()
            cur.execute(f"SELECT EXISTS(SELECT * FROM users WHERE username = '{name}');")
            dbresponse = cur.fetchall()
            if dbresponse[0][0] == 0:
                print("xd")
                hashPass = generate_password_hash(passw, method="sha256", salt_length=10)
                print(type(hashPass))
                cur.execute(f"INSERT INTO users (username, password) VALUES ('{name}', '{hashPass}');")
                mysql.connection.commit()
                cur.close()
            else:
                print("Username already exists.")
    return render_template("login.html")


@app.route("/inzerat/<xd>")
def inzerat(xd):
    return xd


@app.route("/test")
def test():
    return "test"


@app.route("/admin")
def admin():
    return "admin"


if __name__ == "__main__":
    app.run(port=5000, debug=True)