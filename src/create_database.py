import sqlite3
import contextlib
from pathlib import Path
from data_team import Team_Data

def create_connection(db_file: str):
    """ Create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


def create_table(db_file: str):
    """ Create a table for users """
    query = '''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            fullname TEXT NOT NULL,
            age INTEGER,
            preferred_location,
            profile_picture TEXT
        );
    ''' 
    conn = create_connection(db_file)
    if conn is not None:
        with contextlib.closing(conn) as conn:
            with conn:
                conn.execute(query)         

def setup_database(name: str):
    if Path(name).exists():
        print('\033[92mDatabase exists. No action required.\033[0m')
        return

    create_table(name)
    print('\033[91m', 'Creating new example database "users.db"', '\033[0m')

# Database for events
def create_event_database():
    conn = sqlite3.connect('events.db')
    cur = conn.cursor()

    # Create a table to store event data
    cur.execute('''CREATE TABLE IF NOT EXISTS events (
          event_id INTEGER PRIMARY KEY,
          event_title TEXT UNIQUE NOT NULL,
          sport_type TEXT NOT NULL,
          num_players INTEGER NOT NULL,
          playing_level TEXT NOT NULL,
          start_time TEXT NOT NULL,
          end_time TEXT NOT NULL,
          location TEXT NOT NULL,
          description TEXT NOT NULL,
          gender_preference TEXT NOT NULL
        )''')


    conn.commit()
    conn.close()

# Function to insert default event data into the database
# Function to insert default event data into the database
def insert_default_data():
    conn = sqlite3.connect('events.db')
    cur = conn.cursor()

    # Check if there are any entries in the events table
    cur.execute('SELECT COUNT(*) FROM events')
    count = cur.fetchone()[0]

    # If the count is 0, indicating that there are no entries, insert default data
    if count == 0:
        # Get default event data
        team_data = Team_Data()

        # Insert each event into the database
        for event in team_data:
            cur.execute('''INSERT INTO events (event_title, sport_type, num_players, playing_level, start_time, end_time, location, description, gender_preference)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (event['event_title'], event['sport_type'], event['num_players'], event['playing_level'], event['start_time'],
                    '\n'.join(event['end_time']), event['location'], '\n'.join(event['description']), '\n'.join(event['gender_preference'])))

    conn.commit()
    conn.close()


# Function to retrieve event data from the database
def get_event_data():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()

    # Retrieve all events from the database
    c.execute('SELECT * FROM events')
    events = c.fetchall()

    conn.close()

    return events

