from flask import Blueprint, render_template, redirect, url_for
home = Blueprint('home', __name__, url_prefix='/')

# TODO DO NOT EDIT
@home.route('/')
def index():
    return render_template("login.html")

@home.route('/authentication', methods=['GET','POST'])
def authentication():
    return redirect(url_for("home.dashboard"))

@home.route('/register', methods=['GET','POST'])
def register():
    return render_template("register.html")

@home.route('/dashboard', methods=['GET','POST'])
def dashboard():
    return render_template("home.html")

@home.route('/logout', methods=['GET','POST'])
def logout():
    return redirect(url_for("home.index"))