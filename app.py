from flask import Flask, render_template
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "LETSGOSPORT"
limiter = Limiter(
    get_remote_address, app=app, default_limits=["3/second"]
)


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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
