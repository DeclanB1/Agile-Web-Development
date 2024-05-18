import unittest
from app import app, db, User, Events
from utils import set_session
from flask import session
from flask_testing import TestCase
from werkzeug.security import generate_password_hash
from datetime import datetime

class AppTest(TestCase):
    def create_app(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        # Create the database and tables
        db.create_all()

        # Add a sample user
        password_hash = generate_password_hash('password', method='pbkdf2:sha256')
        user = User(username='testuser', email='test@example.com', password=password_hash, fullname='Test User')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        # Remove the session and drop all tables
        db.session.remove()
        db.drop_all()

    # This one passed
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    # This one passed
    def test_register_user(self):
        response = self.client.post('/register', data=dict(
            username='newuser',
            email='newuser@example.com',
            password='password',
            confirm_password='password',
            fullname='New User',
            age=25,
            preferred_location='Crawley'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration Successful!', response.data)

    # This one passed
    def test_registration_duplicate_username(self):
        response = self.client.post('/register', data=dict(
            username='testuser',
            email='newemail@example.com',
            password='password123',
            confirm_password='password123',
            fullname='Existing User',
            age=25,
            preferred_location='Test Location',
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username already in use, please choose a different name.', response.data)     

    # This one passed
    def test_registration_duplicate_email(self):
        # First, register a user
        self.client.post('/register', data=dict(
            username='existinguser',
            email='test@example.com',
            password='password123',
            confirm_password='password123',
            fullname='Existing User',
            age=30,
            preferred_location='Existing Location',
        ), follow_redirects=True)

        # Try to register another user with the same email
        response = self.client.post('/register', data=dict(
            username='newusername',
            email='test@example.com',
            password='password123',
            confirm_password='password123',
            fullname='New User',
            age=25,
            preferred_location='Test Location',
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already in use, please choose a different email.', response.data)


    # This one passed
    def test_login_user(self):
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    # This one passed
    def test_login_wrong_password(self):
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='wrongpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login Unsuccessful. Please check username and password', response.data)

    # This one passed
    def test_login_nonexistent_user(self):
        response = self.client.post('/login', data=dict(
            username='nonexistent',
            password='password123'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login Unsuccessful. Please check username and password', response.data)

    # This one passed
    def test_post_event(self):
        self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        
        response = self.client.post('/post-an-event', data=dict(
            event_title='Test Event',
            sport_type='Soccer',
            num_players=10,
            playing_level='Intermediate',
            event_date='2024-05-29',
            start_time='08:00',
            end_time='10:00',
            location='Morley',
            description='Bring your water bottle',
            gender_preference='Mixed',
            contact_information='Email: email@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Event successfully created', response.data)
        self.assertIn(b'Event Posted Successfully!', response.data)


    # This one passed
    def test_post_event_duplicate_title(self):
        login_response = self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        # Post the first event
        response = self.client.post('/post-an-event', data=dict(
            event_title='Test Event',
            sport_type='Soccer',
            num_players=10,
            playing_level='Intermediate',
            event_date='2024-05-29',
            start_time='08:00',
            end_time='10:00',
            location='Morley',
            description='Bring your water bottle',
            gender_preference='Mixed',
            contact_information='Email: email@example.com'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Event successfully created', response.data)

        # Try to post a duplicate event with duplicate title
        response = self.client.post('/post-an-event', data=dict(
            event_title='Test Event',
            sport_type='Soccer',
            num_players=10,
            playing_level='Intermediate',
            event_date='2024-05-30',
            start_time='08:00',
            end_time='10:00',
            location='Morley',
            description='Bring your water bottle',
            gender_preference='Mixed',
            contact_information='Email: email@example.com'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Event title is already in use. Please choose a different title.', response.data)

    # This one passed
    def test_post_event_missing_fields(self):
        self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)

        response = self.client.post('/post-an-event', data=dict(
            event_title='UWA Tennis League',
            sport_type='Tennis',
            num_players=10,
            playing_level='',
            event_date='2024-05-29',
            start_time='08:00',
            end_time='10:00',
            location='Test Location',
            description='This is a test event.',
            gender_preference='Mixed',
            contact_information='test@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This field is required.', response.data)

    # This one passed
    def test_browse_events(self):
        event = Events(
            event_title='Basketball Game', 
            sport_type='Basketball', 
            num_players=5, 
            playing_level='Beginner',
            event_date='2024-05-30',
            start_time='15:00',
            end_time='17:00',
            location='Downtown Gym',
            description='Just for fun', 
            gender_preference='Male', 
            contact_information='contact@example.com',
            username='testuser'
        )
        db.session.add(event)
        db.session.commit()

        response = self.client.get('/browse-events')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Basketball Game', response.data)

    # This one passed
    def test_browse_single_event(self):
        # Create a sample event
        with self.app.app_context():
            event = Events(
                event_title='Test Event',
                sport_type='Soccer',
                num_players=10,
                playing_level='Intermediate',
                event_date='2024/05/29',
                start_time='08:00 AM',
                end_time='10:00 AM',
                location='Test Location',
                description='This is a test event.',
                gender_preference='Mixed',
                contact_information='test@example.com',
                username='testuser'
            )
            db.session.add(event)
            db.session.commit()

            event_id = event.event_id  # Capture the event ID within the context

        response = self.client.get(f'/browse-single-event/{event_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Event', response.data)

    # This one passed
    def test_profile_page(self):
        self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test User', response.data)

    # This one passed
    def test_edit_profile(self):
        self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        
        response = self.client.post('/edit_profile', data=dict(
            email='newemail@example.com',
            fullname='New Name',
            age='30',
            preferred_location='San Francisco'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your profile has been updated.', response.data)

    # This one passed
    def test_remove_profile_picture(self):
        self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        
        response = self.client.post('/remove_profile_picture', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile picture has been removed.', response.data)

    # This one passed
    def test_edit_event(self):
        with self.client:
            self.client.post('/login', data=dict(
                username='testuser',
                password='password'
            ), follow_redirects=True)

            # Create an event to edit
            with app.app_context():
                event = Events(
                    event_title='Basketball Game',
                    sport_type='Basketball',
                    num_players=5,
                    playing_level='Beginner',
                    event_date='2024-05-30',
                    start_time='10:00',
                    end_time='12:00',
                    location='Downtown Gym',
                    description='Exciting game!',
                    gender_preference='Male',
                    contact_information='contact@example.com',
                    username='testuser'
                )
                db.session.add(event)
                db.session.commit()
                event_id = event.event_id

            response = self.client.post(f'/edit_event/{event_id}', data=dict(
                event_title='Updated Game',
                sport_type='Basketball',
                num_players=5,
                playing_level='Beginner',
                event_date='2024-05-30',
                start_time='10:00',
                end_time='12:00',
                location='Downtown Gym',
                description='Updated description',
                gender_preference='Male',
                contact_information='contact@example.com'
            ), follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Event updated successfully!', response.data)

    # This one passed
    def test_delete_event(self):
        self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        
        event = Events(
            event_title='Basketball Game', 
            sport_type='Basketball', 
            num_players=5, 
            playing_level='Beginner',
            event_date='2024-05-30',
            start_time='15:00',
            end_time='17:00',
            location='Downtown Gym',
            description='Just for fun', 
            gender_preference='Male', 
            contact_information='contact@example.com',
            username='testuser'
        )
        db.session.add(event)
        db.session.commit()
        
        response = self.client.post(f'/delete_event/{event.event_id}', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Event deleted successfully!', response.data)

if __name__ == '__main__':
    unittest.main()