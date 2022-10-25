from datetime import datetime
from diary import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Entry(db.Model):
    entry_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    entry_text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    related_project = db.Column(db.Text)
    tags = db.Column(db.Text)

    def __repr__(self):
        return f"Entry('{self.date}', '{self.entry_text}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    entry = db.relationship('Entry', backref='user', lazy=True)
    is_admin=db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    project_title = db.Column(db.Text, nullable=False)
    project_description = db.Column(db.Text)
    project_type = db.Column(db.Text)
    total_words_goal = db.Column(db.Integer)
    total_words_current = db.Column(db.Integer)
    weekly_words_goal = db.Column(db.Integer)
    weekly_words_current = db.Column(db.Integer)
    google_drive = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Entry('{self.project_title}', '{self.project_description}')"
