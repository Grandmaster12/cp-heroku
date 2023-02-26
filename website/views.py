from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import models
from . import db

# Importing the important functions from the other code file
from CP_func import new_char, OpenAIcall

views = Blueprint("views", __name__)

# these first three pages will be fairly static and won't change much
@views.route("/")
def home():
    return render_template("home.html", user=current_user)

@views.route("/about")
def about():
    return render_template("about.html", user=current_user)

@views.route("/contact")
def contact():
    return render_template("contact.html", user=current_user)

# generate characters using the pre-added information, from the PHB and the motivations, personalities, and moods.
@views.route("/generator", methods=["POST", "GET"])
@login_required
def generate():
    if request.method == "POST":

        # getting the data from the form that is submitted to /generator
        print(request.form)
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

        # calling the function that actually generates the new character with the current user inputs
        rand_chars = new_char(input_params, request.form["num_chars"])

        # taking the output of the randomised character and adding it to the DB
        for ind, rand_char in enumerate(rand_chars):
            char = models.Character(
                char_name = rand_char["Name"],
                char_class = rand_char["Class"],
                char_race = rand_char["Race"],
                char_bg = rand_char["Background"],
                char_motiv = rand_char["Motivation"],
                char_align = rand_char["Alignment"],

                # the randomiser function returns lists for these two features 
                # if they are randomly generated and strings if the user defined them
                char_personality = ", ".join(rand_char["Personality"]) if type(rand_char["Personality"]) == list else rand_char["Personality"],
                char_mood = ", ".join(rand_char["Mood"]) if type(rand_char["Mood"]) == list else rand_char["Mood"],

                user_id = current_user.id
                )

            try:
                db.session.add(char)
                db.session.commit()
            except:
                flash(f"Issue with creating character #{ind + 1}", category="danger")
            
        return redirect(url_for("views.generate"))

    else:
        # display the lists of generated entries in reverse order with the newest ones on top
        texts_enum = list(enumerate(current_user.ai_texts))
        chars_enum = list(enumerate(current_user.characters))
        return render_template("generator.html", user=current_user, chars = list(reversed(chars_enum)), texts=list(reversed(texts_enum)))

# call AI to output some feature descriptions
@views.route("/generator-ai", methods=["POST"])
@login_required
def generate_ai():
    # store the category (i.e. feature) that is requested and the content of the prompt
    category, prompt = request.form["text_cat"], request.form["user_prompt"]

    # if user selected Other, don't add the template and just use the prompt by itself
    # otherwise insert the category into the template
    new_prompt = \
        prompt if category == "other" \
        else f"Create a detailed {category} description for a Dungeons & Dragons character using the following information: " + prompt

    # make a call to the AI using the updated prompt
    result = OpenAIcall(new_prompt)

    # creating the entry into the DB
    text_entry = models.AIText(
        # store the category and the information that the user provided
        prompt = f"({category}), " + prompt,

        # get the output as a result of the call to the AI.
        content = result,
        user_id = current_user.id
        )

    try:
        db.session.add(text_entry)
        db.session.commit()
    except:
        flash(f"Issue with generating AI response", category="danger")

    return redirect(url_for("views.generate"))

# deleting one of the generated characters
@views.route("/delete/<int:id>")
@login_required
def delete(id):
    char_to_del = models.Character.query.get_or_404(id)
    if char_to_del.user_id == current_user.id:
        try:
            db.session.delete(char_to_del)
            db.session.commit()
            return redirect(url_for("views.generate"))
        except:
            flash("There was a problem with deleting that character", category="danger")
            return redirect(url_for("views.generate"))
    flash("Character deleted!", category="success")

# the option to delete all characters if they would like
@views.route("/delete-all/")
@login_required
def delete_all():
    # delete characters one at a time, and 
    for char in current_user.characters:
            try:
                db.session.delete(char)
                db.session.commit()
            except:
                flash(f"There was a problem with deleting character #{char.id}", category="danger")
    flash("All characters deleted!", category="success")
    return redirect(url_for("views.generate"))

# delete all the AI calls - endpoint has to be typed in manually
# it's intended to be only for me when testing layouts and functionality
@views.route("/delete-all-_AI_/")
@login_required
def delete_all_AI():
    for call in current_user.ai_texts:
            try:
                db.session.delete(call)
                db.session.commit()
            except:
                flash("There was a problem with deleting one of the calls", category="danger")
    flash("All calls deleted!", category="success")
    return redirect(url_for("views.generate"))

# the character editor, to allow users to change some of the features that have already been stored
@views.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    edit_char = models.Character.query.get_or_404(id)

    # the POST request is when the user wants to send updates to their current character
    if request.method == "POST":
        # reassigning values for the stored character
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
            return redirect(url_for("views.generate"))
        except:
            flash("There was a problem editing the character's attributes")

    # the GET request is when the user wants to open the editor
    else:
        return render_template("edit.html", char = edit_char, user=current_user)
