from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, validators
from pathlib import Path
from utils import login_required
import os
import time

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_sync.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Set the folder for profile pictures
UPLOAD_FOLDER = 'static/profile-pictures'
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
    profile_picture = db.Column(db.String, default='images/default-profile-pic.png')

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', fullname='{self.fullname}')>"


# Event Model Definition
class Events(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_title = db.Column(db.String, nullable=False)
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
    username = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

    __table_args__ = (
        UniqueConstraint('event_id'),
        UniqueConstraint('event_title')
    )

    def __repr__(self):
        return f"<Events(event_id='{self.event_id}', event_title='{self.event_title}', sport_type='{self.sport_type}', num_players='{self.num_players}', event_date='{self.event_date}', start_time='{self.start_time}', end_time='{self.end_time}', location='{self.location}', description='{self.description}', gender_preference='{self.gender_preference}', contact_information='{self.contact_information}', username='{self.username}')>"

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

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

class EditProfileForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    fullname = StringField('Full Name', [validators.DataRequired()])
    age = IntegerField('Age', [validators.Optional()])
    preferredlocation = StringField('Preferred Location', [validators.Optional()])
    submit = SubmitField('Save Changes')

from flask_wtf.file import FileField, FileAllowed

class EditProfilePictureForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Upload Picture')

class RemoveProfilePictureForm(FlaskForm):
    submit = SubmitField('Remove Profile Picture')

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta

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

# Routes and Logic
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
        file = request.files['profile_picture']
        if file and file.filename != '':
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{username}_{int(time.time())}{ext}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            profile_picture_path = f'profile-pictures/{filename}'
        else:
            profile_picture_path = 'images/default-profile-pic.png'

        new_user = User(
            username=username,
            password=password,
            email=email,
            fullname=fullname,
            age=age,
            preferredlocation=preferredlocation,
            profile_picture=profile_picture_path
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

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

# Post an event
@app.route('/post-an-event', methods=['GET', 'POST'])
@login_required
def post_an_event():
    form = EventForm()
    username = session.get('username')

    if form.validate_on_submit():
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
            contact_information=contact_information,
            username=username
        )

        db.session.add(event)
        db.session.commit()
        return render_template('event_posted_successfully.html', event=event)

    return render_template('post_an_event.html', form=form)

# Browse all events
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
        flash("Error occurred while fetching events")
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
            flash("Event not found")
            # Pass None for event when the event is not found
            return render_template('browse_single_event.html', event=None)
        
    except Exception as e:
        flash("Error occurred while fetching event details")
        return render_template('browse_single_event.html', event=None)

# Display User Profile
@app.route('/profile')
@login_required
def profile():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    events = Events.query.filter_by(username=username).all()
    remove_picture_form = RemoveProfilePictureForm()

    if user:
        return render_template('profile.html', user=user, events=events, form=remove_picture_form)
    else:
        flash('User not found', 'error')
        return redirect(url_for('dashboard'))

# Edit User Profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if request.method == 'GET':
        form.email.data = user.email
        form.fullname.data = user.fullname
        form.age.data = user.age
        form.preferredlocation.data = user.preferredlocation

    if form.validate_on_submit():
        user.email = form.email.data
        user.fullname = form.fullname.data
        user.age = form.age.data
        user.preferredlocation = form.preferredlocation.data

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', form=form)

# Edit User Profile Picture
from werkzeug.utils import secure_filename

@app.route('/edit_profile_picture', methods=['GET', 'POST'])
@login_required
def edit_profile_picture():
    form = EditProfilePictureForm()
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if form.validate_on_submit():
        file = request.files['profile_picture']
        if file and file.filename != '':
            # Delete the old profile picture if it's not the default picture
            old_picture = user.profile_picture
            if old_picture != 'images/default-profile-pic.png':
                old_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(old_picture))
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)

            # Save the new profile picture with a unique filename
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{username}_{int(time.time())}{ext}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            profile_picture_path = f'profile-pictures/{filename}'
            user.profile_picture = profile_picture_path
            db.session.commit()
            flash('Your profile picture has been updated.', 'success')
            return redirect(url_for('profile'))

    return render_template('edit_profile_picture.html', form=form)

# Remove User Profile Picture
@app.route('/remove_profile_picture', methods=['POST'])
@login_required
def remove_profile_picture():
    form = RemoveProfilePictureForm()
    if form.validate_on_submit():
        username = session.get('username')
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Delete the old profile picture if it's not the default picture
            if user.profile_picture != 'images/default-profile-pic.png':
                old_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(user.profile_picture))
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)
            
            # Set the profile picture to the default picture
            user.profile_picture = 'images/default-profile-pic.png'
            db.session.commit()
            flash('Profile picture has been removed.', 'success')
        
        return redirect(url_for('profile'))
    else:
        flash('Failed to remove profile picture.', 'error')
        return redirect(url_for('profile'))


# Main Entry Point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
