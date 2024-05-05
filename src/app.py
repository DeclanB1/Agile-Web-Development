import sqlite3
import contextlib
import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import (
    Flask, render_template, 
    request, session, redirect, url_for
)

from create_database import setup_database
from utils import login_required, set_session
from data_team import Team_Data
from data_person import Person_Data

from wtforms import StringField, SelectField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

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
    if request.method == 'GET':
        return render_template('login.html')

    # Set data to variables
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Attempt to query associated user data
    query = 'select username, password, email from users where username = :username'

    with contextlib.closing(sqlite3.connect(database)) as conn:
        with conn:
            account = conn.execute(query, {'username': username}).fetchone()

    if not account: 
        return render_template('login.html', error='Username does not exist')

    # Verify password
    try:
        ph = PasswordHasher()
        ph.verify(account[1], password)
    except VerifyMismatchError:
        return render_template('login.html', error='Incorrect password')

    # Check if password hash needs to be updated
    if ph.check_needs_rehash(account[1]):
        query = 'update set password = :password where username = :username'
        params = {'password': ph.hash(password), 'username': account[0]}

        with contextlib.closing(sqlite3.connect(database)) as conn:
            with conn:
                conn.execute(query, params)

    # Set cookie for user session
    set_session(
        username=account[0], 
        email=account[2], 
        remember_me='remember-me' in request.form
    )
    
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # Store data to variables 
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')
    username = request.form.get('username')
    email = request.form.get('email')

    # Verify data
    if len(password) < 8:
        return render_template('register.html', error='Your password must be 8 or more characters')
    if password != confirm_password:
        return render_template('register.html', error='Passwords do not match')
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        return render_template('register.html', error='Username must only be letters and numbers')
    if not 3 < len(username) < 26:
        return render_template('register.html', error='Username must be between 4 and 25 characters')

    query = 'select username from users where username = :username;'
    with contextlib.closing(sqlite3.connect(database)) as conn:
        with conn:
            result = conn.execute(query, {'username': username}).fetchone()
    if result:
        return render_template('register.html', error='Username already exists')

    # Create password hash
    pw = PasswordHasher()
    hashed_password = pw.hash(password)

    query = 'insert into users(username, password, email) values (:username, :password, :email);'
    params = {
        'username': username,
        'password': hashed_password,
        'email': email
    }

    with contextlib.closing(sqlite3.connect(database)) as conn:
        with conn:
            result = conn.execute(query, params)

    # We can log the user in right away since no email verification
    set_session( username=username, email=email)
    return redirect('/')

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
