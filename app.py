from flask import Flask, render_template, session, request, redirect, flash, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timedelta, datetime
from database import *
import os

app = Flask(__name__)
app.secret_key = X[2]["secret"]
limiter = Limiter(get_remote_address, app=app, default_limits=["10/second"])
sched = BackgroundScheduler(daemon=True)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=2)


@app.get("/")
def home_get():
    images = sorted(os.listdir(app.static_folder + "/carousel"))
    api_key = X[1]["api_key"]
    spaces = get_space()
    return render_template(
        "index.html", api_key=api_key, spaces=spaces, images=images, nav="home"
    )


@app.get("/admin/spaces")
def admin_court():
    if session.get("roles"):
        spaces = get_space()
        return render_template("admin/spaces.html", spaces=spaces, nav="admin")
    return redirect("/login")


@app.post("/admin/spaces")
def admin_court_post():
    name = request.form["name"]
    phone = request.form["phone"]
    location = request.form["location"]
    types = request.form["type"]
    lat = request.form["latitude"]
    long = request.form["longitude"]
    hours = request.form["hours"]
    slotcar = request.form.get("slotcar")
    slotmotor = request.form.get("slotmotor")
    pricecar = request.form.get("pricecar")
    pricemotor = request.form.get("pricemotor")
    pay = request.form["pay"]
    image = request.files["image"]
    hiddeninfo = request.form["info"]
    filename = name + ".png"
    if hiddeninfo == "edit":
        date = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    else:
        date = datetime.now().strftime("%Y%m%d")
    if image:
        image.save(app.static_folder + "/spaces/" + filename)
    set_space(
        name,
        types,
        phone,
        filename,
        location,
        lat,
        long,
        hours,
        pay,
        date,
        slotcar,
        slotmotor,
        pricecar,
        pricemotor,
    )
    return redirect("/admin/spaces")


@app.get("/admin/spaces/<name>")
def admin_spaces_get(name):
    space = get_space_name(name)
    return render_template("/admin/editspace.html", space=space, nav="admin")


@app.get("/spaces")
def courts_get():
    spaces = get_space()
    return render_template("/spaces/spaces.html", spaces=spaces, nav="spaces")


@app.get("/spaces/<name>")
def spaces_get(name):
    space = get_space_name(name)
    today = datetime.now().strftime("%Y%m%d")
    return render_template(
        "/spaces/viewspace.html", space=space, today=today, nav="spaces"
    )


@app.post("/spaces/<name>")
def spaces_post(name):
    session["booking"] = request.form["mynum"]
    session["booktype"] = request.form["mine"]
    return redirect(url_for("booking_get", name=name))


@app.get("/booking/<name>")
def booking_get(name):
    if session.get("token") and session.get("booking") and session.get("booktype"):
        space = get_space_name(name)
        return render_template("/booking/booking.html", space=space)
    session.pop("booking")
    session.pop("booktype")
    return redirect("/spaces")


@app.post("/booking/<name>")
def booking_post(name):
    methods = request.form["payment"]
    now = datetime.now().timestamp()
    space = get_space_name(name)
    today = datetime.now().strftime("%Y%m%d")
    if session["booktype"] == "mobil":
        update_slot(
            name,
            today,
            {"slotcar": int(space["slot"][today]["slotcar"]) - int(session["booking"])},
        )
    elif session["booktype"] == "motor":
        update_slot(
            name,
            today,
            {
                "slotmotor": int(space["slot"][today]["slotmotor"])
                - int(session["booking"])
            },
        )
    make_booking(session, int(now), today, name, methods)
    session.pop("booking")
    session.pop("booktype")
    return redirect(url_for("QRIS", name=int(now)))


@app.get("/profile")
def profile_get():
    data = get_user(session["email"])
    booking = get_booking(session["email"])
    if booking:
        booking = dict(reversed(dict(booking).items()))
    return render_template("profile.html", data=data, booking=booking, nav="profile")


@app.post("/profile")
def profile_post():
    name = request.form["nameInput"]
    data = {"name": name}
    update_user(session["email"], data)
    return redirect("/profile")


@app.get("/login")
def login_get():
    if session.get("token"):
        return redirect("/profile")
    return render_template("/login/login.html", nav="login")


@app.get("/forgot")
def forgot_get():
    return render_template("/login/forgot.html")


@app.post("/forgot")
def forgot_post():
    email = request.form["email"]
    res = forgot(email)
    flash(res)
    return redirect("/forgot")


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
    acc = X[1]
    if acc["email"] == email and acc["password"] == password:
        session["roles"] = "superuser"
        return redirect("/admin/spaces")
    flash("Email atau Password Salah")
    return redirect("/login/admin")


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


@app.get("/QRIS/<name>")
def QRIS(name):
    return render_template("QRIS.html", name=name)


@app.get("/admin/spaces/delete/<name>")
def delete_spaces_get(name):
    image_path = os.path.join(app.static_folder, "spaces", name + ".png")
    if os.path.exists(image_path):
        os.remove(image_path)
    delete_space(name)
    return redirect("/admin/spaces")


@app.get("/cancel/<book>/<items>")
def cancel(book, items):
    booking = eval(items)
    if booking["status"] == "Belum Dibayar":
        change_booking_status(session["email"], book)
        slot = get_space_slot(booking["space_name"], int(booking["dates"]))
        if booking["tipe"] == "mobil":
            data = {"slotcar": slot["slotcar"] + int(booking["qty"])}
        elif booking["tipe"] == "motor":
            data = {"slotmotor": slot["slotmotor"] + int(booking["qty"])}
        update_slot(booking["space_name"], booking["dates"], data)
    return redirect("/profile")


@app.get("/paid/<book>")
def paid(book):
    change_booking_status(session["email"], book, "Sudah Dibayar")
    return redirect(url_for("QRIS", name=book))


def update_daily():
    spaces = get_space()
    for name, space in spaces.items():
        tmwr = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        if space["type"] == "mobil":
            update_slot(name, tmwr, {"slotcar": space["car"]})
        elif space["type"] == "motor":
            update_slot(name, tmwr, {"slotmotor": space["motor"]})
        else:
            update_slot(
                name, tmwr, {"slotcar": space["car"], "slotmotor": space["motor"]}
            )
        remove_slot(name, (datetime.now() - timedelta(days=5)).strftime("%Y%m%d"))
        print(name + " Updated " + tmwr)


sched.add_job(update_daily, CronTrigger(hour=12, minute=39))
sched.start()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
