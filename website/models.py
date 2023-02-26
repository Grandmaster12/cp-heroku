from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# creating all the DB models, describing the tables, their respective columns, 
# types of info and relationships between tables

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=True)
    
    # list of characters each user created, referenced by ids in characters table
    characters = db.relationship("Character")

    # stores the user's text AI calls
    ai_texts = db.relationship("AIText")

# storing the characters that the user has created
class Character(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    char_name = db.Column(db.String, nullable=False)
    char_class = db.Column(db.String, nullable=False)
    char_race = db.Column(db.String, nullable=False)
    char_bg = db.Column(db.String, nullable=False)
    char_motiv = db.Column(db.String, nullable=False)
    char_align = db.Column(db.String, nullable=False)
    char_personality = db.Column(db.String, nullable=False)
    char_mood = db.Column(db.String, nullable=False)

    # storing the user who created this character using the primary key col in user table
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Name: %r>" % self.char_name

# storing the text created by the user 
# it will become a template model to use for image + audio generation
class AIText(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    prompt = db.Column(db.String)
    content = db.Column(db.String)

    # linking the user to the specific entry
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))