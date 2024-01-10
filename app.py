from flask import Flask, render_template, session, request, redirect, flash
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from datetime import date
from database import login, register, set_user, get_user, update_user

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
    return render_template("profile.html", data=data)


@app.post("/profile")
def profile_post():
    name = request.form["name"]
    age = request.form["age"]
    interest = request.form["interest"]
    data = {"name": name, "age": age, "interest": interest}
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
    if log_in[0]:
        session["token"] = log_in[1]
        session["email"] = email
        return redirect("/")
    else:
        session.clear()
        return redirect("/login")


@app.get("/register")
def register_get():
    return render_template("register.html")


@app.post("/register")
def register_post():
    email = request.form["email"]
    name = request.form["name"]
    age = date.today().year - int(request.form["age"])
    interest = request.form["interest"]
    password = request.form["password"]

    if get_user(email):
        flash("Email already taken")
        return redirect("/register")
    else:
        message = register(email, password)
        set_user(email, password, name, age, interest)
        flash(message)
        return redirect("/login")

@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
