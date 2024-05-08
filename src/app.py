import sqlite3
import contextlib
import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import (
    Flask, render_template, 
    request, session, redirect, url_for, flash
)

from create_database import setup_database
from utils import login_required, set_session
from data_team import Team_Data
from data_person import Person_Data

from wtforms import StringField, SelectField, IntegerField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from wtforms.validators import Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    preferredlocation = StringField('Preferred Location', validators=[DataRequired()])
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

app = Flask(__name__)
app.secret_key = 'xpSm7p5bgJY8rNoBjGWiz5yjxM-NEBlW6SIBI62OkLc='

database = "users.db"
setup_database(name=database)

Team_Data = Team_Data()
Person_Data = Person_Data()


# @app.route('/')
# @login_required
# def index():
#     print(f'User data: {session}')
#     return render_template('index.html', username=session.get('username'))
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
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        with contextlib.closing(sqlite3.connect(database)) as conn:
            with conn:
                account = conn.execute('SELECT username, password, email FROM users WHERE username = ?', (username,)).fetchone()

        if not account:
            flash('Username does not exist', 'error')
            return render_template('login.html', form=form)

        try:
            ph = PasswordHasher()
            if ph.verify(account[1], password):
                if ph.check_needs_rehash(account[1]):
                    new_hash = ph.hash(password)
                    conn.execute('UPDATE users SET password = ? WHERE username = ?', (new_hash, username))

                session['logged_in'] = True 
                session['username'] = account[0]
                session['email'] = account[2]
                return redirect('/')

        except VerifyMismatchError:
            flash('Incorrect password', 'error')

    return render_template('login.html', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        fullname = form.fullname.data
        age = form.age.data
        preferredlocation = form.preferredlocation.data

        # Check if username already exists
        with contextlib.closing(sqlite3.connect(database)) as conn:
            with conn:
                if conn.execute('SELECT username FROM users WHERE username = ?', (username,)).fetchone():
                    flash('Username already exists', 'error')
                    return render_template('register.html', form=form)

        # Hash the password
        hashed_password = PasswordHasher().hash(password)

        # Insert the new user data into the database
        with contextlib.closing(sqlite3.connect(database)) as conn:
            with conn:
                conn.execute('INSERT INTO users (username, password, email, fullname, age, preferredlocation) VALUES (?, ?, ?, ?, ?, ?)',
                             (username, hashed_password, email, fullname, age, preferredlocation))

        # Log the user in right after registration
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
