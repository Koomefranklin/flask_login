import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, url_for, flash, render_template, session
from passlib.hash import sha256_crypt
from sqlalchemy.exc import IntegrityError
# import logging
# from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)
app.secret_key = "secretKey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = datetime.timedelta(minutes=5)
db = SQLAlchemy(app)


class Login(db.Model):
    f_name = db.Column(db.String(100))
    s_name = db.Column(db.String(100))
    email = db.Column(db.String(100), primary_key = True)
    password = db.Column(db.String(255))
    salt = db.Column(db.String(255))


    def __init__(self, f_name, l_name, email, password, salt):
        self.email = email
        self.f_name = f_name
        self.l_name = l_name
        self.password = password
        self.salt = salt
    

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = Login.query.filter(Login.email == email).first()
        user_salt = user.salt
        saltedSecret = password + user_salt
        if sha256_crypt.verify(saltedSecret, user.password):
            session['user'] = user
            flash("Login Successfull")
            return redirect(url_for('home'))
        else:
            flash("Wrong email or password")
            return render_template("login.html", title="Login")
    else:
        return render_template("login.html", title="Login")


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        f_name = request.form['f-name']
        s_name = request.form['s-name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        salt = random.shuffle(list(string.ascii_letters + string.digits))

        if len(f_name) > 0 and len(s_name) > 0 and len(email) > 0 and \
            len(password) > 0 and len(password2) > 0:
            if password2 == password:
                salted_password = password + salt
                hashed_password = sha256_crypt.hash(salted_password)
                newUser = Login(f_name, s_name, email, hashed_password, salt)
                db.session.add(newUser)
                db.session.commit()

                flash("User Registered Sussessfully! Login")
                return redirect(url_for("login"))
            else:
                flash("Passwords do not match!")
                return render_template("signup.html", title="Signup")
    else:
        return render_template("signup.html", title="Signup")


@app.route("/")
def home():
    return render_template("index.html", title="HomePage")


@app.errorhandler(404)
def page_not_found(error):
    return url_for('home')


if __name__ == "__main__":
    with app.app_context:
        db.create_all()
    app.run(debug=True)
