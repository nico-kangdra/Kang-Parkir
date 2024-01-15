from flask import Flask, render_template, session, request, redirect, flash
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from datetime import date
from database import login, register, set_user, get_user, update_user, set_court, get_court
import json

app = Flask(__name__)
app.secret_key = "LETSGOSPORT"
limiter = Limiter(get_remote_address, app=app, default_limits=["3/second"])


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=2)


@app.get("/")
def home_get():
    images = sorted(os.listdir(app.static_folder + "/carousel"))
    return render_template("index.html", images=images)


@app.get("/admin/court")
def admin_court():
    if session.get("roles"):
        courts = get_court()
        return render_template("admin/courts.html", courts=courts)
    return redirect("/")

@app.post("/admin/court")
def admin_court_post():
    name = request.form["name"]
    phone = request.form["phone"]
    location = request.form["location"]
    types = request.form["type"]
    image = request.files["image"]
    if image:
        image.save(app.static_folder + "/courts/" + image.filename)
    set_court(name, location, types, phone, image.filename)
    return redirect("/admin/court")

@app.get("/admin/user")
def admin_user():
    if session.get("roles"):
        return render_template("admin/user.html")
    return redirect("/")

@app.get("/courts")
def courts_get():
    images = sorted(os.listdir(app.static_folder + "/courts"))
    return render_template("courts.html", images=images)


@app.get("/booking")
def booking_get():
    return render_template("booking.html")


@app.get("/profile")
def profile_get():
    data = get_user(session["email"])
    year = date.today().year
    age = year - int(data["data"]["born"])
    return render_template("profile.html", data=data, year=year, age=age)


@app.post("/profile")
def profile_post():
    name = request.form["name"]
    born = request.form["born"]
    interest = request.form["interest"]
    data = {"name": name, "born": born, "interest": interest}
    update_user(session["email"], data)
    return redirect("/profile")


@app.get("/login")
def login_get():
    return render_template("login.html")


@app.post("/login")
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    log_in = login(email, password)
    if type(log_in) == str:
        flash(log_in)
    elif not log_in[0]:
        flash("Please Verify Your Account by click the link from Email")
    else:
        session["token"] = log_in[1]
        session["email"] = email
        return redirect("/")
    return redirect("/login")


@app.get("/login/admin")
def login_admin_get():
    return render_template("admin/login.html")


@app.post("/login/admin")
def login_admin_post():
    email = request.form["email"]
    password = request.form["password"]
    # log_in = login(email, password)
    f = open("account.json")
    acc = json.load(f)
    if acc["email"] == email and acc["password"] == password:
        session["roles"] = "superuser"
        return redirect("/admin/court")
    return redirect("/logout")


@app.get("/register")
def register_get():
    year = date.today().year
    return render_template("register.html", year=year)


@app.post("/register")
def register_post():
    email = request.form["email"]
    name = request.form["name"]
    born = request.form["born"]
    interest = request.form["interest"]
    password = request.form["password"]

    if get_user(email):
        flash("Email already taken")
        return redirect("/register")
    else:
        message = register(email, password)
        set_user(email, password, name, born, interest)
        flash(message)
        return redirect("/login")


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
