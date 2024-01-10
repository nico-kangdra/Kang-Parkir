import pyrebase
from hashlib import sha256
import json
f = open("config.json")
config = json.load(f)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


def register(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        return "Verfication has been sent"
    except:
        return "There's an error"

def login(email, password):
    user = auth.sign_in_with_email_and_password(email, password)
    return auth.get_account_info(user["idToken"])['users'][0]['emailVerified']


def set_user(email: str, password: str, name: str, age: int, interest: str):
    data = {
        "email": email,
        "password": sha256(password.encode()).hexdigest(),
        "name": name,
        "age": age,
        "interest": interest,
    }
    db.child("users").set(data)

# def get_image():

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
