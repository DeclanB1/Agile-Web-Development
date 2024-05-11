##====================================================================================================
## Import Dependancies
##====================================================================================================

import os
import sqlite3
import contextlib
import uuid

from flask import (
    Flask, render_template, 
    request, session, redirect, flash
)

from werkzeug.security import check_password_hash, generate_password_hash

from create_database import setup_database
from utils import login_required
from data_team import Team_Data
from data_person import Person_Data

from wtforms import StringField, SelectField, IntegerField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Email, EqualTo, Optional
    

##====================================================================================================
## Forms Definition
##====================================================================================================


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[Optional()])
    preferredlocation = StringField('Preferred Location', validators=[Optional()])
    profile_picture = FileField('Update Profile Picture', validators=[Optional(),FileAllowed(ALLOWED_EXTENSIONS)])
    submit = SubmitField('Register')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired()])
    sport_type = SelectField('Sport Type', choices=[('basketball', 'Basketball'), ('soccer', 'Soccer'), ('rugby', 'Rugby')], validators=[DataRequired()])
    num_players = IntegerField('Number of Players Needed', validators=[DataRequired()])
    start_time = StringField('Event Start Time (e.g., DD/MM/YYYY HH:MM)', validators=[DataRequired()])
    end_time = StringField('Event End Time (e.g., DD/MM/YYYY HH:MM)', validators=[DataRequired()])
    location = StringField('Event Location', validators=[DataRequired()])
    description = TextAreaField('Description of Event', validators=[DataRequired(), Length(max=200)])
    gender_preference = SelectField('Gender Preference', choices=[('male', 'Male'), ('female', 'Female'), ('mixed', 'Mixed')], validators=[DataRequired()])
    submit = SubmitField('Post Event')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')

##====================================================================================================
## App Configuration
##====================================================================================================

app = Flask(__name__)
app.secret_key = 'xpSm7p5bgJY8rNoBjGWiz5yjxM-NEBlW6SIBI62OkLc='

UPLOAD_FOLDER = '/profile-images'  # Update the upload folder path

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'profile-images')  # Update the upload folder configuration
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure the upload folder exists

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

##====================================================================================================
## Database Configuration
##====================================================================================================

database = "users.db"
setup_database(name=database)

Team_Data = Team_Data()
Person_Data = Person_Data()

##====================================================================================================
## Routes Definition
##====================================================================================================


@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', team_data=Team_Data, person_data=Person_Data)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(request.referrer or '/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Assuming LoginForm is defined elsewhere
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        with contextlib.closing(sqlite3.connect(database)) as conn:
            account = conn.execute('SELECT username, password, email FROM users WHERE username = ?', (username,)).fetchone()

        if not account:
            flash('Username does not exist', 'error')
            return render_template('login.html', form=form)

        if check_password_hash(account[1], password):
            session['logged_in'] = True
            session['username'] = account[0]
            session['email'] = account[2]
            return redirect('/')
        else:
            flash('Incorrect password', 'error')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Assuming RegistrationForm is defined elsewhere
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        fullname = form.fullname.data
        age = form.age.data
        preferredlocation = form.preferredlocation.data

        # Process file upload
        filename = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):  # Assuming allowed_file is defined
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

        # Hash the password using Werkzeug
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert the new user
        with contextlib.closing(sqlite3.connect(database)) as conn:
            if conn.execute('SELECT username FROM users WHERE username = ?', (username,)).fetchone():
                flash('Username already exists', 'error')
                return render_template('register.html', form=form)

            conn.execute('INSERT INTO users (username, password, email, fullname, age, preferredlocation, profile_picture) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (username, hashed_password, email, fullname, age, preferredlocation, filename))
            conn.commit()

        # Log the user in
        session['logged_in'] = True
        session['username'] = username
        session['email'] = email
        return redirect('/dashboard')

    return render_template('register.html', form=form)

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

@app.route('/post-an-event', methods=['GET', 'POST'])
@login_required
def post_event():
    form = EventForm()
    if form.validate_on_submit():
        event = {
            'title': form.title.data,
            'sport_type': form.sport_type.data,
            'num_players': form.num_players.data,
            'start_time': form.start_time.data,
            'end_time': form.end_time.data,
            'location': form.location.data,
            'description': form.description.data,
            'gender_preference': form.gender_preference.data
        }
        # Assuming saving to database is handled elsewhere

        return render_template('event_posted_successfully.html', event=event)

    return render_template('post_an_event.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
