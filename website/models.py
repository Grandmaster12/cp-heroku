from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Character(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    char_name = db.Column(db.String(100), nullable=False)
    char_class = db.Column(db.String(100), nullable=False)
    char_race = db.Column(db.String(100), nullable=False)
    char_bg = db.Column(db.String(100), nullable=False)
    char_motiv = db.Column(db.String(100), nullable=False)
    char_align = db.Column(db.String(100), nullable=False)
    char_personality = db.Column(db.String(100), nullable=False)
    char_mood = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default = func.now())

    # storing the user who created this character using the primary key col in user table
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Task %r>" % self.id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=True)
    first_name = db.Column(db.String(100), unique=False)
    # list of characters each user created, referenced by ids in characters table
    characters = db.relationship("Character")