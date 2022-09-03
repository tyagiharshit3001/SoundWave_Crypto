from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from sqlhelper import *
from forms import *
from functools import wraps
from credentials import *
import time

# import mysql.connector
"""
Flask is a web application framework written in python.
Flask is based on: WSGI, Werkzeug and Jinja2 Template Engine
    WSGI is a specification for universal interface between web server and web application.
    Werkzeug is WSGI toolkit which implement request, response object and other utility functions.
    Jinja2 Template engine: Popular Templating engine for python.
"""

app = Flask(__name__)

app.config['MYSQL_HOST'] = h_host
app.config['MYSQL_USER'] = h_username
app.config['MYSQL_PASSWORD'] = h_password
app.config['MYSQL_DB'] = h_database
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized access to page is denied. Please Log In first.", 'danger')
            return render_template('login.html')

    return wrap


def is_logged_out(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('log_out'))
        else:
            return redirect(url_for('dashboard'))

    return wrap


def log_in_user(username):
    users = Table('users', 'name', 'email', 'username', 'password')
    user = users.get_val("username", username)
    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')


@app.route('/log_out', methods=['POST', 'GET'])
@is_logged_in
def log_out():
    session.clear()
    flash("You have log out Successfully", 'success')
    return redirect(url_for('login'))


@app.route("/dashboard", methods=['POST', 'GET'])
@is_logged_in
def dashboard():
    form = SendMoneyForm(request.form)
    balance = get_balance(session.get('username'))
    blockchain = get_blockchain().chain
    trans_time = time.strftime('%I:%M %p')
    return render_template('dashboard.html', balance=balance, form=form, session=session, trans_time=trans_time, blockchain=blockchain, page='dashboard' )


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")
    # print(request.method, form.validate(), isNewUser(form.username.data))
    # print(form.name.data, form.email.data, form.username.data, form.password.data)
    # print(bool(form.name.validators), bool(form.email.validators), bool(form.username.validators), bool(form.password.validators))
    # if form is submitted
    if request.method == 'POST' and form.validate():
        # collect form data
        username = form.username.data
        email = form.email.data
        name = form.name.data
        # make sure user does not already exist
        if isNewUser(username):
            # add the user to mysql and log them in
            password = sha256_crypt.encrypt(form.password.data)
            users.insert_in(name, email, username, password)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html', form=form, page='register')


@app.route("/transaction", methods=['GET', 'POST'])
@is_logged_in
def transaction():
    form = SendMoneyForm(request.form)
    balance = get_balance(session.get('username'))
    if request.method == 'POST':
        try:
            send_money(session.get('username'), form.username.data, form.amount.data)
            flash("SoundWave Crypto sent!!!", 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('transaction'))

    return render_template('transaction.html', balance=balance, form=form, page='transaction')


@app.route('/buy', methods=['GET', 'POST'])
@is_logged_in
def buy():
    form = BuyForm(request.form)
    balance = get_balance(session.get('username'))
    if request.method == 'POST':
        try:
            send_money('Bank', session.get('username'), form.amount.data)
            flash("SoundWave Crypto Purchased!!!", 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('buy'))

    return render_template('buy.html', balance=balance, form=form, page='buy')


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html', page='index')


@app.route("/login", methods=['GET', 'POST'])
def login():
    # send_money("Bank", "prashanttyagi985", 1)
    # print(request.method)
    if request.method == 'POST':
        username = request.form['username']
        candidate = request.form['password']
        users = Table("users", "name", "email", "username", "password")
        user = users.get_val("username", username)
        acc_pass = user.get("password")
        if acc_pass is None:
            flash("Username doen't exist.", 'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(candidate, acc_pass):
                log_in_user(username)
                flash("Log in Successful", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password!!!")
                return redirect(url_for(login))
    return render_template('login.html', page='login')
    # users = Table('users', 'name', 'email', 'username', 'password')
    # users.insert_in('jaggah', 'jd@gmail.com', 'jdname', 'password')


if __name__ == "__main__":
    app.secret_key = h_secret_Key
    app.run(debug=True)
