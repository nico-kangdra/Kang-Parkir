import pyrebase
from hashlib import sha256
import json

f = open("config.json")
config = json.load(f)[0]

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


def encode(var):
    return sha256(var.encode("utf-8")).hexdigest()


def register(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user["idToken"])
        return "Verfication link has been sent to your Email"
    except:
        return "There's an error occured"
    
def forgot(email):
    try:
        auth.send_password_reset_email(email)
        return "Reset link has been sent to your Email"
    except:
        return "Email not Found"

def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email,password)
        user = auth.refresh(user["refreshToken"])
        return (auth.get_account_info(user["idToken"])["users"][0]["emailVerified"], user["idToken"])
    except:
        return "Email or Password is wrong"

def set_user(email, password, name):
    data = {
        "email": email,
        "password": encode(password),
        "name": name,
    }
    db.child("users").child(encode(email)).update(data)


def get_user(email):
    return db.child("users").child(encode(email)).get().val()

def update_user(email, data: dict):
    db.child("users").child(encode(email)).update(data)


def set_space(space_name, type, phone, image_filename, link, lat, long, open_hours, pay, date, slotcar="", slotmotor="", pricecar="", pricemotor=""):
    data = {
        "name": space_name,
        "type": type,
        "phone": phone,
        "image": image_filename,
        "long": long,
        "lat": lat,
        "link": link,
        "hours": open_hours,
        "pricecar": pricecar,
        "pricemotor": pricemotor,
        "pay": pay,
        "car": slotcar,
        "motor": slotmotor,
    }
    dates = {
        "slotcar": slotcar,
        "slotmotor": slotmotor,
    }

    db.child("spaces").child(space_name).update(data) 
    update_slot(space_name, date, dates)

def update_slot(space_name, date, data):
    db.child("spaces").child(space_name).child("slot").child(date).update(data)

def get_space():
    spaces = db.child("spaces").get().val()
    return spaces

def get_space_name(name):
    space = db.child("spaces").child(name).get().val()
    return space

def delete_space(name):
    db.child("spaces").child(name).remove()

def make_booking(session, now, timeout, space, method):
    data = {
        "timeout": timeout,
        "space_name": space,
        "method": method,
        "qty": session['booking'],
        "tipe": session['booktype'],
        "status": "Belum Dibayar"
    }
    db.child("users").child(encode(session['email'])).child('order').child(now).set(data)

def get_booking(email):
    book = db.child("users").child(encode(email)).child("order").get().val()
    return book

def change_booking_status(email, now, status="Dibatalkan"):
    db.child("users").child(encode(email)).child("order").child(now).update({"status": status})

a = get_booking("nkangdra@gmail.com")
print(a)