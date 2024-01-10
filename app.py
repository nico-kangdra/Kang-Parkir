from flask import Flask, render_template, session
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "LETSGOSPORT"
limiter = Limiter(
    get_remote_address, app=app, default_limits=["3/second"]
)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=2)

@app.get("/")
def main():
    images = sorted(os.listdir(app.static_folder + "/carousel"))
    return render_template("index.html", images=images)


@app.get("/courts")
def courts():
    images = sorted(os.listdir(app.static_folder + "/courts"))
    return render_template("courts.html", images=images)


@app.get("/booking")
def booking():
    return render_template("booking.html")

@app.get("/profile")
def profile():
    return render_template("profile.html")

@app.get("/login")
def login():
    return render_template("login.html")

@app.get("/register")
def register():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
