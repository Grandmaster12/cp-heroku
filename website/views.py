from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import models
from . import db
from CP_func import new_char

views = Blueprint("views", __name__)

@views.route("/", methods=["POST", "GET"])
@login_required
def index():
    if request.method == "POST":
        input_params = [
            request.form["init_name"],
            request.form["init_class"],
            request.form["init_race"],
            request.form["init_bg"],
            request.form["init_motiv"],
            request.form["init_align"],
            request.form["init_personality"],
            request.form["init_mood"],
            ]

        rand_chars = new_char(input_params, request.form["num_chars"])
        for ind, rand_char in enumerate(rand_chars):
            char = models.Character(
                char_name = rand_char["Name"],
                char_class = rand_char["Class"],
                char_race = rand_char["Race"],
                char_bg = rand_char["Background"],
                char_motiv = rand_char["Motivation"],
                char_align = rand_char["Alignment"],
                char_personality = ", ".join(rand_char["Personality"]) if type(rand_char["Personality"]) == list else rand_char["Personality"],
                char_mood = ", ".join(rand_char["Mood"]) if type(rand_char["Mood"]) == list else rand_char["Mood"],
                user_id = current_user.id
                )

            try:
                db.session.add(char)
                db.session.commit()
            except:
                flash(f"Issue with creating character #{ind + 1}", category="danger")
        return redirect(url_for("views.index"))

    else:
        char_list = models.Character.query.order_by(models.Character.date.desc()).all()
        return render_template("index.html", chars=char_list, user=current_user)

@views.route("/delete/<int:id>")
@login_required
def delete(id):
    char_to_del = models.Character.query.get_or_404(id)
    if char_to_del.user_id == current_user.id:
        try:
            db.session.delete(char_to_del)
            db.session.commit()
            return redirect(url_for("views.index"))
        except:
            flash("There was a problem with deleting that character", category="danger")
    flash("Character deleted!", category="success")

@views.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    edit_char = models.Character.query.get_or_404(id)
    if request.method == "POST":
        edit_char.char_name = request.form["name"]
        edit_char.char_class = request.form["class"]
        edit_char.char_race = request.form["race"]
        edit_char.char_bg = request.form["bg"]
        edit_char.char_motiv = request.form["motiv"]
        edit_char.char_align = request.form["align"]
        edit_char.char_personality = request.form["personality"]
        edit_char.char_mood = request.form["mood"]

        try:
            db.session.commit()
            return redirect(url_for("views.index"))
        except:
            flash("There was a problem editing character attributes")
    else:
        return render_template("edit.html", char = edit_char, user=current_user)
