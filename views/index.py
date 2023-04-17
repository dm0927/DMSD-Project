from flask import Blueprint, render_template, redirect, url_for, request, flash
from sql.db import DB
from flask_bcrypt import Bcrypt

home = Blueprint('home', __name__, url_prefix='/')

bcrypt = Bcrypt()

# TODO DO NOT EDIT
@home.route('/')
def index():
    return render_template("login.html")

@home.route('/authentication', methods=['GET','POST'])
def authentication():
    return redirect(url_for("home.dashboard"))

@home.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        if password == confirmpassword:
            hash = bcrypt.generate_password_hash(password)
            result = DB.insertOne("""
                    INSERT INTO CUSTOMER(Name,Email,Phone,Password)
                    VALUES(%s,%s,%s,%s)
                    """, fullname, email, phone, hash)
            if result.status:
                flash("User Created.", "success")    
                return redirect(url_for("home.index"))
        else:
            flash("Password and Confirm Password aren't same.", "warning")
    return render_template("register.html")

@home.route('/dashboard', methods=['GET','POST'])
def dashboard():
    return render_template("home.html")

@home.route('/logout', methods=['GET','POST'])
def logout():
    return redirect(url_for("home.index"))