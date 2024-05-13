from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, validators
from pathlib import Path
import os

from data_team import Team_Data
from data_person import Person_Data

Team_Data = Team_Data()
Person_Data = Person_Data()

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Set the folder for profile pictures
UPLOAD_FOLDER = 'profile-pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# User Model Definition
class User(db.Model):
    __tablename__ = 'users'
    
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    preferredlocation = db.Column(db.String)
    profile_picture = db.Column(db.String)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', fullname='{self.fullname}')>"

# LoginForm Definition
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# RegistrationForm Definition
class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=8)])
    confirm_password = PasswordField('Confirm Password', [validators.EqualTo('password'), validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    fullname = StringField('Full Name', [validators.DataRequired()])
    age = IntegerField('Age', [validators.Optional()])
    preferredlocation = StringField('Preferred Location', [validators.Optional()])
    profile_picture = StringField('Profile Picture', [validators.Optional()])
    submit = SubmitField('Register')

# EventForm Definition
class EventForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    sport_type = StringField('Sport Type', [validators.DataRequired()])
    num_players = IntegerField('Number of Players', [validators.DataRequired()])
    start_time = StringField('Start Time', [validators.DataRequired()])
    end_time = StringField('End Time', [validators.DataRequired()])
    location = StringField('Location', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    gender_preference = StringField('Gender Preference', [validators.DataRequired()])
    submit = SubmitField('Post Event')

# Routes and Logic
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', team_data=Team_Data, person_data=Person_Data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password, form.password.data):
            session['logged_in'] = True
            session['username'] = user.username
            session['email'] = user.email
            if form.remember.data:
                session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        email = form.email.data
        fullname = form.fullname.data
        age = form.age.data
        preferredlocation = form.preferredlocation.data
        
        # Process the uploaded file
        file = request.files['profile_picture']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            file_path = None  # Use a default image path or handle as no image

        new_user = User(
            username=username,
            password=password,
            email=email,
            fullname=fullname,
            age=age,
            preferredlocation=preferredlocation,
            profile_picture=file_path
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully!')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('dashboard'))

@app.route('/post-an-event', methods=['GET', 'POST'])
def post_event():
    form = EventForm()
    if form.validate_on_submit():
        # Process the form data and potentially save it to the database
        flash('Event posted successfully!')
        return render_template('event_posted_successfully.html', event=form.data)

    return render_template('post_an_event.html', form=form)

@app.route('/team-basketball')
def team_basketball():
    return render_template('team_basketball.html', team_data=Team_Data)

@app.route('/team-football')
def team_football():
    return render_template('team_football.html', team_data=Team_Data)

@app.route('/team-baseball')
def team_baseball():
    return render_template('team_baseball.html', team_data=Team_Data)

@app.route('/person-basketball')
def person_basketball():
    return render_template('person_basketball.html', person_data=Person_Data)

@app.route('/person-tennis')
def person_tennis():
    return render_template('person_tennis.html', person_data=Person_Data)

@app.route('/person-golf')
def person_golf():
    return render_template('person_golf.html', person_data=Person_Data)

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

# Main Entry Point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
