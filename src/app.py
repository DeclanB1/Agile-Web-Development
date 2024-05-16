##===============================================================================================================================
## Import Dependancies
##===============================================================================================================================

import os
from datetime import datetime, timedelta
from config import Config

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, validators
from wtforms.validators import DataRequired, EqualTo

from utils import login_required


##===============================================================================================================================
## Initialise Flask Application and SQLAlchemy
##===============================================================================================================================

# Initialise Flask App
app = Flask(__name__)
app.config.from_object(Config) # Import Secret Key from .env file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_sync.db' # Label Application db as sport_sync.db 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise SQLAlchemy
db = SQLAlchemy(app)

# Set the folder for profile pictures
UPLOAD_FOLDER = 'profile-pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

##===============================================================================================================================
## Define User Models
##===============================================================================================================================

# Generates User db Model
class User(db.Model):
    __tablename__ = 'users'
    
    username = db.Column(db.String, primary_key=True) # Username is set as Primary Key
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer) #Optional Field
    preferredlocation = db.Column(db.String) #Optional Field
    profile_picture = db.Column(db.String) #Optional Field

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', fullname='{self.fullname}')>"

# Generates Events db Model    
class Events(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True) # Event ID is a primary key
    event_title = db.Column(db.String, nullable=False) # All Fields are necessary not optional
    sport_type = db.Column(db.Integer, nullable=False)
    num_players = db.Column(db.Integer, nullable=False)
    playing_level = db.Column(db.String, nullable=False)
    event_date = db.Column(db.String, nullable=False)
    start_time = db.Column(db.String, nullable=False)
    end_time = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    gender_preference = db.Column(db.String, nullable=False)
    contact_information = db.Column(db.String, nullable=False)   

    __table_args__ = (
        UniqueConstraint('event_id'),
        UniqueConstraint('event_title')
    )

    def __repr__(self):
        return f"<Events(event_id='{self.event_id}', event_title='{self.event_title}', sport_type='{self.sport_type}', num_players='{self.num_players}', event_date='{self.event_date}', start_time='{self.start_time}', end_time='{self.end_time}', location='{self.location}', description='{self.description}', gender_preference='{self.gender_preference}', contact_information='{self.contact_information}')>"

##===============================================================================================================================
## Forms Definition
##===============================================================================================================================

# LoginForm Definition
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# RegistrationForm Definition
class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()]) #minimum username length set to 4 char, max 25 char
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=8)]) #minimum password length 8 char
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Password entries do not match. Please try again') #Flash Error Message
    ])    
    email = StringField('Email', [validators.DataRequired(), validators.Email()]) # ensure valid email entry
    fullname = StringField('Full Name', [validators.DataRequired()])
    age = IntegerField('Age', [validators.Optional()])
    preferredlocation = StringField('Preferred Location', [validators.Optional()])
    profile_picture = StringField('Profile Picture', [validators.Optional()])
    submit = SubmitField('Register')

# EventForm Definition
class EventForm(FlaskForm):
    event_title = StringField('Event Title', validators=[DataRequired()])
    sport_type = SelectField('Sport Type', choices=[('Basketball', 'Basketball'), ('Soccer', 'Soccer'), ('Tennis', 'Tennis')], validators=[DataRequired()])
    num_players = StringField('Number of Players Needed', validators=[DataRequired()])
    playing_level = SelectField('Playing Level', choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], validators=[DataRequired()])
    event_date = StringField('Event Date', validators=[DataRequired()], render_kw={'type': 'date'})
    start_time = SelectField('Event Start Time', choices=[], validators=[DataRequired()])
    end_time = SelectField('Event End Time', choices=[], validators=[DataRequired()])
    location = StringField('Event Location', validators=[DataRequired()])
    description = StringField('Description of Event', validators=[DataRequired()])
    gender_preference = SelectField('Gender Preference', choices=[('Male', 'Male'), ('Female', 'Female'), ('Mixed', 'Mixed')], validators=[DataRequired()])
    contact_information = StringField('Contact Information', validators=[DataRequired()])
    submit = SubmitField('Post Event')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        # Populate time choices for start time and end time fields
        self.start_time.choices = self._generate_time_choices()
        self.end_time.choices = self._generate_time_choices()

    def _generate_time_choices(self):
        choices = []
        start_time = datetime.strptime('00:00', '%H:%M')
        end_time = datetime.strptime('23:30', '%H:%M')

        while start_time <= end_time:
            formatted_time = start_time.strftime('%I:%M %p')  # Format time as 1 pm
            choices.append((start_time.strftime('%H:%M'), formatted_time))
            start_time += timedelta(minutes=30)

        return choices

##===============================================================================================================================
## Define Routes and Logic
##===============================================================================================================================

# Home Page/ Dashboard Route as default
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Register New Account Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create an instance of the registration form
    form = RegistrationForm()
    
    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Retrieve form data
        username = form.username.data
        # Hash the password using PBKDF2 with SHA-256
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        email = form.email.data
        fullname = form.fullname.data
        age = form.age.data
        preferredlocation = form.preferredlocation.data

        # Handle profile picture upload
        file = request.files['profile_picture']
        if file and file.filename != '':
            # Secure the filename and save the file to the upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            # If no file is uploaded, set file_path to None
            file_path = None

        # Create a new user instance with the form data and file path
        new_user = User(
            username=username,
            password=password,
            email=email,
            fullname=fullname,
            age=age,
            preferredlocation=preferredlocation,
            profile_picture=file_path
        )

        try:
            # Add the new user to the database
            db.session.add(new_user)
            db.session.commit()
            # Flash success message and redirect to login page
            flash('Registration Successful!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            # Rollback the session in case of an integrity error (e.g., username already exists)
            db.session.rollback()
            # Flash error message
            flash('Username already in use, please choose a different name.', 'error')
    
    # Render the registration template with the form
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Create an instance of the login form
    form = LoginForm()
    
    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Query the database for a user with the provided username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if the user exists and if the password is correct
        if user and check_password_hash(user.password, form.password.data):
            # Set session variables to indicate the user is logged in
            session['logged_in'] = True
            session['username'] = user.username
            session['email'] = user.email
            
            # Handle 'remember me' functionality
            if form.remember.data:
                session.permanent = True
            
            # Redirect to the dashboard after successful login
            return redirect(url_for('dashboard'))
        else:
            # Flash error message if login is unsuccessful
            flash('Login Unsuccessful. Please check username and password', 'error')
    
    # Render the login template with the form
    return render_template('login.html', form=form)


# Logout Route
@app.route('/logout', methods=['POST'])
def logout():
    # Clear all data stored in the session
    session.clear()
    
    # Redirect to the dashboard page after logging out
    return redirect(url_for('dashboard'))


# How it Works Route
@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

# Post an Event Route
@app.route('/post-an-event', methods=['GET', 'POST'])
# Login required for user to post an event
@login_required
def post_an_event():
    # Create an instance of the event form
    form = EventForm()

    # Check if the form is submitted and valid
    if form.validate_on_submit():
        try:
            # Retrieve form data
            event_title = form.event_title.data
            sport_type = form.sport_type.data
            num_players = form.num_players.data
            playing_level = form.playing_level.data
            event_date = datetime.strptime(form.event_date.data, '%Y-%m-%d').strftime('%Y/%m/%d')
            start_time = datetime.strptime(form.start_time.data, '%H:%M').strftime('%I:%M %p')
            end_time = datetime.strptime(form.end_time.data, '%H:%M').strftime('%I:%M %p')
            location = form.location.data
            description = form.description.data
            gender_preference = form.gender_preference.data
            contact_information = form.contact_information.data

            # Create a new event instance with the form data
            event = Events(
                event_title=event_title,
                sport_type=sport_type,
                num_players=num_players,
                playing_level=playing_level,
                event_date=event_date,
                start_time=start_time,
                end_time=end_time,
                location=location,
                description=description,
                gender_preference=gender_preference,
                contact_information=contact_information
            )
            
            # Add the new event to the database
            db.session.add(event)
            db.session.commit()
            # Flash success message and render success template
            flash('Event successfully created', 'success')
            return render_template('event_posted_successfully.html', event=event)
        
        except IntegrityError:
            # Rollback the session in case of an integrity error (e.g., event title already exists)
            db.session.rollback()
            # Flash error message
            flash('Event title is already in use. Please choose a different title.', 'danger')
    
    # Render the event posting template with the form
    return render_template('post_an_event.html', form=form)

# Browse all events Route
@app.route('/browse-events')
def browse_events():
    try:
        # Fetch all events
        events = Events.query.all()

        # Fetch distinct values for sport type, num players, playing level, and location
        sport_types = db.session.query(Events.sport_type.distinct()).all()
        sport_types = [sport_type[0] for sport_type in sport_types]  # Extracting the first element of each tuple

        num_players = db.session.query(Events.num_players.distinct()).all()
        num_players = [num_player[0] for num_player in num_players]

        playing_levels = db.session.query(Events.playing_level.distinct()).all()
        playing_levels = [playing_level[0] for playing_level in playing_levels]

        locations = db.session.query(Events.location.distinct()).all()
        locations = [location[0] for location in locations]

        # Pass the data to the template
        return render_template('browse_events.html', events=events, sport_types=sport_types, num_players=num_players, playing_levels=playing_levels, locations=locations, username=session.get('username'))
    except Exception as e:
        flash("Error occurred while fetching events") #Flash Error Message
        return render_template('browse_events.html')

# Browse single event
@app.route('/browse-single-event/<int:event_id>')
def browse_single_event(event_id):
    try:
        # Retrieve the event from the database based on its event_id
        event = Events.query.filter_by(event_id=event_id).first()

        # Check if the event exists
        if event:
            return render_template('browse_single_event.html', event=event)
        else:
            flash("Event not found") #Flash Error Message
            # Pass None for event when the event is not found
            return render_template('browse_single_event.html', event=None)
        
    except Exception as e:
        flash("Error occurred while fetching event details") #Flash Error Message
        return render_template('browse_single_event.html', event=None)

##===============================================================================================================================
## Main Entry Point
##===============================================================================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)