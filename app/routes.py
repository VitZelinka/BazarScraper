from flask import render_template, request
from app import app

@app.route('/')
@app.route('/home')
def index():
    user = {'username': 'Kokt'}
    return render_template("index.html", title="XD", user=user)


@app.route("/login")
@app.route("/register")
def auth():
    return "login/register"


@app.route("/inzerat/<xd>")
def inzerat(xd):
    return xd


@app.route("/test")
def test():
    print(request.args.get("kys"))
    return "test"

@app.route("/admin")
def admin():
    return "admin"