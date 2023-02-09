from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import models
from . import db


auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = models.User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                first = user.first_name
                flash(f"Login successful! Welcome back, {first}!", category ="success")
                login_user(user, remember=True)
                return redirect(url_for("views.index"))
            else:
                flash("Password is incorrect. Try again", category ="danger")
        else:
            flash("Email does not exist. Sign up or try again", category="danger")

    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # check if user has already made an account
        user = models.User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists. Please login", category="danger")
        elif len(email) < 4:
            flash("Email must be longer than 3 characters", category="danger")
        elif len(first_name) < 2:
            flash("Name must be longer than 1 character", category="danger") 
        elif password1 != password2:
            flash("Passwords don't match", category="danger")
        elif len(password1) < 7:
            flash("Password must be longer than 6 characters", category = "danger") 
        else:
            # add user to DB
            new_user = models.User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method="sha256")
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account successfully created!", category="success")
            return redirect(url_for("views.index"))

    return render_template("sign_up.html", user=current_user)

