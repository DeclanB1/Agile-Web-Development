from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, validators
from pathlib import Path
from utils import login_required
import os



# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_sync.db'
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
    return render_template('dashboard.html')

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

        print(f"Debug: username={username}, email={email}, password={password}, fullname={fullname}, age={age}, preferredlocation={preferredlocation}")

        filename = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                print(f"Debug: Saved file to {file_path}")

        # Hash the password
        hashed_password = PasswordHasher().hash(password)

        # Check if username already exists
        try:
            with contextlib.closing(sqlite3.connect(database)) as conn:
                if conn.execute('SELECT username FROM users WHERE username = ?', (username,)).fetchone():
                    flash('Username already exists', 'error')
                    return render_template('register.html', form=form)

                print("Debug: Inserting into database")
                conn.execute('INSERT INTO users (username, password, email, fullname, age, preferredlocation, profile_picture) VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (username, hashed_password, email, fullname, age, preferredlocation, filename))
                conn.commit()

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            flash(f'A database error occurred: {e}', 'error')
            return render_template('register.html', form=form)

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

# Post an event
@app.route('/post-an-event', methods=['GET', 'POST'])
@login_required
def post_an_event():
    form = EventForm()

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

# Main Entry Point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
