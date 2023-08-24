import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, url_for, flash, render_template, session
from passlib.hash import sha256_crypt
from sqlalchemy.exc import IntegrityError
# import logging
# from flask_mail import Mail, Message
import secrets
import string

app = Flask(__name__)
app.secret_key = "secretKey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.sqlite3'
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
        receivedToken = request.form['token']

        if session['token'] == receivedToken:

            user = Login.query.filter(Login.email == email).first()
            user_salt = user.salt
            saltedSecret = password + user_salt
            if sha256_crypt.verify(saltedSecret, user.password):
                session.pop('token', None)
                session['user'] = user.email
                flash("Login Successfull")
                return redirect(url_for('home'))
            else:
                flash("Wrong email or password")
                return redirect(url_for("login"))
        else:
            flash("Time out try again!")
            return redirect(url_for("login"))
    else:
        characters = list(string.ascii_letters + string.digits)
        token = ''.join(secrets.choice(characters)for _ in range(16))
        session['token'] = token
        return render_template("login.html", title="Login", token=token)


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    characters = list(string.ascii_letters + string.digits)
    if request.method == "POST":
        receivedToken = request.form['token']
        f_name = request.form['f-name']
        s_name = request.form['s-name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        salt = ''.join(secrets.choice(characters) for _ in range(24))
        if session['token'] and session['token'] == receivedToken:
            if len(f_name) > 0 and len(s_name) > 0 and len(email) > 0 and \
                len(password) > 0 and len(password2) > 0:
                if password2 == password:
                    salted_password = password + salt
                    hashed_password = sha256_crypt.hash(salted_password)
                    newUser = Login(f_name, s_name, email, hashed_password, salt)
                    try:
                        db.session.add(newUser)
                        db.session.commit()
                        session.pop('token', None)
                        flash("User Registered Sussessfully! Login")
                        return redirect(url_for("login"))
                    except IntegrityError:
                        flash('Email already used!')
                        return redirect(url_for('signup'))
                    
                else:
                    flash("Passwords do not match!")
                    return redirect(url_for("signup"))
            else:
                flash("All Fields are Required!")
                return redirect(url_for("signup"))
        else:
            flash("Try Again")
            return redirect(url_for("signup"))
    else:
        token = ''.join(secrets.choice(characters)for _ in range(16))
        session['token'] = token
        return render_template("signup.html", title="Signup", token=token)


@app.route("/")
def home():
    try:
        user = session['user']
        if Login.query.filter(Login.email == user):
            return render_template("index.html", title="HomePage")
    except:
        flash("You'll need to login first")
        return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    return url_for('home')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
