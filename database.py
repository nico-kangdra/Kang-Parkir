import pyrebase
from hashlib import sha256
import json

f = open("config.json")
config = json.load(f)[0]

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


def encode(var: str):
    return sha256(var.encode("utf-8")).hexdigest()


def register(email: str, password: str):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user["idToken"])
        return "Verfication link has been sent to your Email"
    except:
        return "There's an error occured"
    
def forgot(email: str):
    try:
        auth.send_password_reset_email(email)
        return "Reset link has been sent to your Email"
    except:
        return "Email not Found"

def login(email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email,password)
        user = auth.refresh(user["refreshToken"])
        return (auth.get_account_info(user["idToken"])["users"][0]["emailVerified"], user["idToken"])
    except:
        return "Email or Password is wrong"

def set_user(email: str, password: str, name: str):
    data = {
        encode(email): {
            "email": email,
            "password": encode(password),
            "name": name,
        }
    }
    db.child("users").update(data)


def get_user(email: str):
    return db.child("users").child(encode(email)).get().val()

def update_user(email: str, data: dict):
    db.child("users").child(encode(email)).update(data)


def set_space(space_name: str, type: str, phone:str, image_filename: str, link:str, lat, long, open_hours:str):
    data = {
        space_name: {
            "name": space_name,
            "type": type,
            "phone": phone,
            "image": image_filename,
            "long": long,
            "lat": lat,
            "link": link,
            "hours": open_hours
        }
    }
    db.child("spaces").update(data) 


def get_space():
    spaces = db.child("spaces").get().val()
    return spaces

def get_space_name(name: str):
    space = db.child("spaces").child(name).get().val()
    return space

def update_space(space: str, data: dict):
    db.child("spaces").child(space).update(data)

def delete_space(name: str):
    db.child("spaces").child(name).remove()