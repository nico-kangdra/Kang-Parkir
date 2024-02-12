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

def login(email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email,password)
        user = auth.refresh(user["refreshToken"])
        return (auth.get_account_info(user["idToken"])["users"][0]["emailVerified"], user["idToken"])
    except:
        return "Email or Password not found"

def set_user(email: str, password: str, name: str, born: int, interest: str):
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
    db.child("users").child(encode(email)).child("data").update(data)


def set_space(space_name: str, type: str, phone:str, image_filename: str, lat, long):
    data = {
        space_name: {
            "name": space_name,
            "type": type,
            "phone": phone,
            "image": image_filename,
            "long": long,
            "lat": lat
        }
    }
    db.child("spaces").update(data) 


def get_space():
    spaces = db.child("spaces").get().val()
    return spaces
# set_space("ParkirW","Car","085155331900","no",-6.903045666023884, 106.88468475647025)
# print(get_space()["ParkirV"]["long"])
def update_space(space: str, data: dict):
    db.child("spaces").child(encode(space)).update(data)


# print(get_court()[0]["image"])
# set_court("Kharisma","Kalideres","null","Badminton","None")
# set_timeslot("Kharisma")
# print(get_court("Kharisma"))
# def get_user(email:str)

# user = register("nkangdra@gmail.com","aaaaaa")
# print(user)
# auth.send_email_verification(user['idToken'])
# user = auth.sign_in_with_email_and_password("nk@gmail.com", "aaaaaa")
# p = auth.get_account_info(user["idToken"])
# print(p['users'][0]['emailVerified'])
# try:
#     urls = storage.child("images/slide.jpg").get_url(user['idToken'])
#     print(urls)
# except:
#     print("Ndak ada")
