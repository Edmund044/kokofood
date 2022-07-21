from flask import Flask, jsonify, render_template, request, url_for, redirect,session,flash
from flask_session import Session
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
import os
from werkzeug.utils import secure_filename

def make_request_to_convert_currency(amount1,  currency1, currency2):
    url = "https://api.apilayer.com/fixer/convert?to=" + \
        currency2+"&from="+currency1+"&amount="+amount1

    payload = {}
    headers = {
        "apikey": "x0CghhnZZ8OA6CB1zkubZU8xhCTK2kWg"
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    status_code = response.status_code
    res = json.loads(response.text)

    return res

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder='../templates',
            static_folder='../static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER            
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)            
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///currency_convertor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(image):
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return os.path.join(app.config['UPLOAD_FOLDER'], filename)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    second_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    picture = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(5), nullable=False)
    wallet_number = db.Column(db.Integer, nullable=False)
    wallet_balance = db.Column(db.Float(20), nullable=False)


@app.route("/")
def index():
    return render_template("signup.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/convert-currency")
def convert():
    return render_template("convert.html")


@app.route("/transfer-money")
def transfer():
    return render_template("transfer.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/signin")
def signin():
    return render_template("signin.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/handle-signup", methods=["POST"])
def handle_signup():
        if request.method == "POST":
            first_name = request.form["first_name"]
            second_name = request.form["second_name"]
            currency = request.form["currency"]
            email = request.form["email"]
            picture =  upload_file(request.files["picture"])
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            wallet_number = randint(123545224, 873648754)
            if password != confirm_password:
                return "Passwords do not match"
            user = User.query.filter_by(email=email).first()
            if user:
                return "User already exists"
            else:
                response = make_request_to_convert_currency(
                    "1000", "USD", currency)
            wallet_balance = response["result"]
            new_user = User(first_name=first_name, second_name=second_name, currency=currency, email=email, picture=picture, wallet_number=wallet_number, wallet_balance=wallet_balance,
                            password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for("signin"))
   

@app.route("/handle-signin", methods=["POST"])
def handle_signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user:
            session["user_id"] = user.id
            session["first_name"] = user.first_name
            session["second_name"] = user.second_name
            session["email"] = user.email
            session["picture"] = user.picture
            session["currency"] = user.currency
            session["wallet_number"] = user.wallet_number
            session["wallet_balance"] = user.wallet_balance

            if check_password_hash(user.password, password):
                return render_template("dashboard.html", first_name=user.first_name, second_name=user.second_name, wallet_number=user.wallet_number, wallet_balance=user.wallet_balance, currency=user.currency, profile_picture=user.picture)
            else:
                return "Password is incorrect"
        else:
            return "User does not exist"


@app.route("/get_transaction", methods=["POST"])
def get_transaction():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

    return render_template("dashboard.html")


@app.route("/handle-profile-update", methods=["POST"])
def handle_profile_update():
    if request.method == "POST":
        first_name = request.form["first_name"]
        second_name = request.form["second_name"]
        currency = request.form["currency"]
        email = request.form["email"]
        id = request.form["id"]
        saved_picture_url = upload_file(request.files["picture"])
        the_user = db.session.query(User).filter(User.id == id ).first()
        response = make_request_to_convert_currency(
                     str(the_user.wallet_balance),the_user.currency, currency)
        the_user.first_name = first_name
        the_user.second_name = second_name
        the_user.currency = currency
        the_user.wallet_balance = response["result"]
        the_user.email = email
        the_user.picture = saved_picture_url    
        db.session.commit()
        session["user_id"] = id
        session["first_name"] = first_name
        session["second_name"] = second_name
        session["email"] = email
        session["picture"] = saved_picture_url
        session["currency"] = currency
        session["wallet_balance"] = response["result"]
    return render_template("dashboard.html")


@app.route("/handle-convert-currency", methods=["POST"])
def handle_convert_currency():
    if request.method == "POST":
        amount1 = request.form["amount1"]
        currency1 = request.form["currency1"]
        currency2 = request.form["currency2"]

    response = make_request_to_convert_currency(amount1, currency1, currency2)
    return render_template("converted-currency.html", amount1=amount1, amount2=response["result"], currency1=currency1, currency2=currency2)


@app.route("/handle-transfer-money", methods=["POST"])
def handle_transfer_money():
    if request.method == "POST":
        amount_to_send = request.form["amount_to_send"]
        receiver_wallet_number = request.form["receiver_wallet_number"]
        sender_wallet_number = request.form["sender_wallet_number"]

    # make sure wallets exists
        sender = User.query.filter_by(
            wallet_number=sender_wallet_number).first()
        receiver = User.query.filter_by(
            wallet_number=receiver_wallet_number).first()
        if receiver:
            if receiver == sender:
             return "Cannot send money to your own wallet"
            transaction_rate_fee = 0.05
            wallet_balance = sender.wallet_balance
            sender_currency = sender.currency
            receiver_currency = receiver.currency
            if float(amount_to_send) + float(amount_to_send) * transaction_rate_fee < wallet_balance:
                transfer_status = "Succesful transfer"
                transaction_cost = float(amount_to_send) * transaction_rate_fee
                response = make_request_to_convert_currency(amount_to_send, sender_currency, receiver_currency)
                amount_to_receive = response["result"]
                new_balance = float(wallet_balance) - (float(amount_to_send) +
                                                    float(amount_to_send) * transaction_rate_fee)                                   
                # update sender wallet
                the_sender = db.session.query(User).filter(User.wallet_number == sender_wallet_number).first()
                the_sender.wallet_balance = new_balance
                db.session.commit()
                session["wallet_balance"] = the_sender.wallet_balance
                # update receiver wallet
                the_receiver = db.session.query(User).filter(User.wallet_number == receiver_wallet_number).first()
                the_receiver.wallet_balance = float(amount_to_receive) + float(receiver.wallet_balance)
                db.session.commit()

            elif float(amount_to_send) + float(amount_to_send) * transaction_rate_fee > wallet_balance:
                transfer_status = "Insufficient funds"
                transaction_cost = 0
                amount_to_receive = 0
                new_balance = wallet_balance
            else:
                transfer_status = "Failed transfer"
                transaction_cost = 0
                new_balance = wallet_balance

            return render_template("transfered-money.html", amount_to_receive=amount_to_receive, wallet_number=receiver_wallet_number, transfer_status=transfer_status, sender_currency=sender_currency, receiver_currency=receiver_currency, new_balance=new_balance, transaction_cost=transaction_cost)
        else:
            return "Wallet does not exist"

@app.route("/health")
def health():
    return {
        "data": {
            "status": "ok",
            "message": "API is up and running"
        }
    }


@app.route("/v1/")
def home():
    return {
        "data": {
            "status": "ok",
            "message": "Welcome to the home page"
        }
    }


@app.route("/v1/currencies")
def currencies():
    return {
        "data": {
            "status": "ok",
            "message": "Welcome to the home page"
        }
    }


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return {
        "status": 404,
        "message": "Page not found"
    }

# Internal Server Error


@app.errorhandler(500)
def page_not_found(e):
    return {
        "status": 500,
        "message": "Internal server errror"
    }

def runServer(host='0.0.0.0'):

    app.run(host)


if __name__ == "__main__":
    try:
        runServer()
    finally:
        app.run()