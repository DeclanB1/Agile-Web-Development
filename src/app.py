from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, validators
from pathlib import Path
import os


# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = '\x1a\xf3\x91F\xe9Y\x85+\xeb\x1a\xf2\xf4\xec\xd2\xe2\xaf\xe8C\xa57\xa5\x1d\xd3X'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
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
    
class Events(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_title = db.Column(db.String, nullable=False)
    sport_type = db.Column(db.Integer, nullable=False)
    num_players = db.Column(db.Integer, nullable=False)
    playing_level = db.Column(db.String, nullable=False)
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
        return f"<Events(event_id='{self.event_id}', event_title='{self.event_title}', sport_type='{self.sport_type}', num_players='{self.num_players}', start_time='{self.start_time}', end_time='{self.end_time}', location='{self.location}', description='{self.description}', gender_preference='{self.gender_preference}', contact_information='{self.contact_information}')>"

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

# EventForm
class EventForm(FlaskForm):
    event_title = StringField('Event Title', [validators.DataRequired()])
    sport_type = SelectField('Sport Type', choices=[('Basketball', 'Basketball'), ('Football', 'Football'), ('Baseball', 'Baseball')])
    num_players = IntegerField('Number of Players Needed', [validators.DataRequired()])
    playing_level = SelectField('Playing Level', choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')])
    start_time = StringField('Event Start Time (e.g., DD/MM/YYYY HH:MM)', [validators.DataRequired()])
    end_time = StringField('Event End Time (e.g., DD/MM/YYYY HH:MM)', [validators.DataRequired()])
    location = StringField('Event Location', [validators.DataRequired()])
    description = TextAreaField('Description of Event', [validators.DataRequired()])
    gender_preference = SelectField('Gender Preference', choices=[('Male', 'Male'), ('Female', 'Female'), ('Mixed', 'Mixed')])
    contact_information = StringField('Contact Information', [validators.DataRequired()])
    submit = SubmitField('Post Event')

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

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

# Post an event
@app.route('/post-an-event', methods=['GET', 'POST'])
def post_an_event():
    form = EventForm()

    if form.validate_on_submit():
        event_title = form.event_title.data
        sport_type = form.sport_type.data
        num_players = form.num_players.data
        playing_level = form.playing_level.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        location = form.location.data
        description = form.description.data
        gender_preference = form.gender_preference.data
        contact_information = form.contact_information.data
            
        event = Events(
            event_title=event_title,
            sport_type=sport_type,
            num_players=num_players,
            playing_level=playing_level,
            start_time=start_time,
            end_time=end_time,
            location=location,
            description=description,
            gender_preference=gender_preference,
            contact_information=contact_information
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
        num_players = db.session.query(Events.num_players.distinct()).all()
        playing_levels = db.session.query(Events.playing_level.distinct()).all()
        locations = db.session.query(Events.location.distinct()).all()

        # Pass the data to the template
        return render_template('browse_events.html', events=events, sport_types=sport_types, num_players=num_players, playing_levels=playing_levels, locations=locations, username=session.get('username'))
    except Exception as e:
        flash("Error occurred while fetching events")
        return render_template('browse_events.html')

# Browse single event
@app.route('/browse-event/<int:event_id>')
def browse_event(event_id):
    try:
        # Retrieve the event from the database based on its event_id
        event = Events.query.filter_by(_event_id=event_id).first()

        # Check if the event exists
        if event:
            return render_template('browse_event.html', event=event)
        else:
            flash("Event not found")
            # Pass None for event when the event is not found
            return render_template('browse_event.html', event=None)
        
    except Exception as e:
        flash("Error occurred while fetching event details")
        return render_template('browse_event.html', event=None)

# Main Entry Point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
