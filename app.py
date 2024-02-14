from flask import Flask, render_template, session, request, redirect, flash
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from database import login, register, set_user, get_user, update_user, set_space, get_space, forgot, get_space_name, delete_space
import json

app = Flask(__name__)
app.secret_key = json.load(open("config.json"))[2]["secret"]
limiter = Limiter(get_remote_address, app=app, default_limits=["10/second"])


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=2)


@app.get("/")
def home_get():
    images = sorted(os.listdir(app.static_folder + "/carousel"))
    f = open("config.json")
    api_key = json.load(f)[1]["api_key"]
    spaces  = get_space()
    return render_template("index.html", api_key=api_key, spaces=spaces, images=images, nav="home")


@app.get("/admin/spaces")
def admin_court():
    if session.get("roles"):
        spaces = get_space()
        return render_template("admin/spaces.html", spaces=spaces, nav="admin")
    return redirect("/")

@app.post("/admin/spaces")
def admin_court_post():
    name = request.form["name"]
    phone = request.form["phone"]
    location = request.form["location"]
    types = request.form["type"]
    lat = request.form["latitude"]
    long = request.form["longitude"]
    hours = request.form["hours"]
    image = request.files["image"]
    filename = name + ".png"
    if image:
        image.save(app.static_folder + "/spaces/" + filename)
    set_space(name, types, phone, filename, location, lat, long, hours)
    return redirect("/admin/spaces")

@app.get("/admin/spaces/<name>")
def admin_spaces_get(name):
    space = get_space_name(name)
    return render_template("/admin/editspace.html", space=space, nav="spaces")

@app.get("/spaces")
def courts_get():
    spaces = get_space()
    return render_template("/spaces/spaces.html", spaces=spaces ,nav="spaces")

@app.get("/spaces/<name>")
def spaces_get(name):
    space = get_space_name(name)
    return render_template("/spaces/editspace.html", space=space, nav="spaces")


@app.get("/booking")
def booking_get():
    return render_template("booking.html")


@app.get("/profile")
def profile_get():
    data = get_user(session["email"])
    return render_template("profile.html", data=data, nav="profile")


@app.post("/profile")
def profile_post():
    name = request.form["nameInput"]
    data = {'name': name}
    update_user(session["email"], data)
    return redirect("/profile")


@app.get("/login")
def login_get():
    return render_template("/login/login.html", nav="login")

@app.get("/forgot")
def forgot_get():
    return render_template("/login/forgot.html")

@app.post("/forgot")
def forgot_post():
    email = request.form["email"]
    res = forgot(email)
    flash(res)
    return redirect('/forgot')

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
    f = open("config.json")
    acc = json.load(f)[1]
    if acc["email"] == email and acc["password"] == password:
        session["roles"] = "superuser"
        return redirect("/admin/spaces")
    return redirect("/logout")


@app.get("/register")
def register_get():
    return render_template("/login/register.html", nav="login")


@app.post("/register")
def register_post():
    email = request.form["email"]
    name = request.form["name"]
    password = request.form["password"]

    if get_user(email):
        flash("Email already taken")
        return redirect("/register")
    else:
        message = register(email, password)
        set_user(email, password, name)
        flash(message)
        return redirect("/login")


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.get("/admin/spaces/delete/<name>")
def delete_spaces_get(name):
    image_path = os.path.join(app.static_folder, 'spaces', name+".png")
    if os.path.exists(image_path):
        os.remove(image_path)
    delete_space(name)
    return redirect("/admin/spaces")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
