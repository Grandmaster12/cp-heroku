from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import models
from . import db

# code for linking and creating the logic for the authentication pages
auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = models.User.query.filter_by(email=email).first()
        if user:

            # password hashing for security so that DB never stores the actual password text
            if check_password_hash(user.password, password):
                username = user.username
                flash(f"Login successful! Welcome back, {username}!", category ="success")
                login_user(user, remember=True)
                return redirect(url_for("views.generate"))
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
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # check if user has already made an account
        user = models.User.query.filter_by(email=email).first()

        # potential failure conditions for incorrect signing up
        if user:
            flash("Email already exists. Please login", category="danger")
        elif len(email) < 4:
            flash("Email must be longer than 3 characters", category="danger")
        elif len(username) < 2:
            flash("Name must be longer than 1 character", category="danger") 
        elif password1 != password2:
            flash("Passwords don't match", category="danger")
        elif len(password1) < 7:
            flash("Password must be longer than 6 characters", category = "danger") 
        else:

            # if user can successfully be signed up, add them to the DB
            new_user = models.User(
                email=email,
                username=username,
                password=generate_password_hash(password1, method="sha256")
            )

            db.session.add(new_user)
            db.session.commit()

            # log them in after signing them up
            login_user(new_user, remember=True)
            flash(f"Account successfully created! Welcome, {username}!", category="success")
            return redirect(url_for("views.generate"))

    return render_template("sign_up.html", user=current_user)

