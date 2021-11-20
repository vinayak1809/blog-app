from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login.utils import confirm_login
from sqlalchemy.orm import session
from werkzeug.utils import secure_filename
from . import db
from .models import User, Admin_user
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("emaill")
        password = request.form.get("passwordd")

        usert = User.query.filter_by(email=email).first()
        admin_user = Admin_user.query.filter_by(email=email).first()
        if usert:
            if check_password_hash(usert.password, password):
                flash("Logged in!", category='success')
                login_user(usert, remember=True)
                return redirect(url_for('views.not_login'))
            else:
                flash('Password is incorrect.', category='error')

        elif admin_user:
            if admin_user.password == password:
                flash("Logged in!", category='success')
                login_user(admin_user, remember=True)
                return redirect(url_for('views.admin_post'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

            return render_template("signup.html", user=current_user, signin="Sign In")

    return render_template("signup.html", user=current_user, signin="Sign In")


@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')

        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('auth.login'))

    return render_template("signup.html", user=current_user, signup="Sign Up")


@auth.route("/update_profile")
@auth.route("/update_profile/<username>", methods=['POST', 'GET'])
@login_required
def update_profile(username):
    user = current_user
    user = User.query.filter_by(username=current_user.username).first()
    if request.method == "POST":

        birthday = request.form.get('birthday')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        about = request.form.get('about')

        img = request.files['image']
        j = img.read()
        user.user_img = j
        user.birth_date = birthday
        user.about = about

        if len(password) < 6:
            flash('Password is too short.', category='error')
        elif password != confirm_password:
            flash('Password don\'t match!', category='error')
        else:

            user.password = generate_password_hash(password, method='sha256')

        db.session.commit()

    return render_template("update_profile.html", user=current_user)


@auth.route("/delete_acc/<username>")
def delete_acc(username):
    usern = username.replace("%20", " ")
    user = User.query.filter_by(username=usern).first()

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('views.home'))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.not_login"))
