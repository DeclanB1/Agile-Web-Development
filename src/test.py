import sqlite3

def create_event_database():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()

    # Create a table to store event data
    c.execute('''CREATE TABLE IF NOT EXISTS events (
          event_id INTEGER PRIMARY KEY,
          event_title TEXT NOT NULL,
          sport_type TEXT NOT NULL,
          num_players INTEGER NOT NULL,
          skill_level_required TEXT NOT NULL,
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
    c = conn.cursor()

    # Get default event data
    team_data = Team_Data()

    # Insert each event into the database
    for event in team_data:
        c.execute('''INSERT INTO events (event_title, sport_type, num_players, skill_level_required, start_time, end_time, location, description, gender_preference)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (event['event_title'], event['sport_type'], event['num_players'], event['skill_level_required'], event['start_time'],
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

def Team_Data():
  team_data = [
    { 
      'event_title': "Downtown Ballers' basketball event",
      'sport_type': 'Basketball',
      'num_players': 2,
      'skill_level_required': 'Intermediate',
      'start_time': '25/05/2024 13:00',
      'end_time': '25/05/2024 15:00',
      'location': 'City Park, Downtown',
      'description': ['Looking for players aged 18-30',
                       'Preferably with experience playing guard or forward positions',
                       'Must be committed to attending practices and games regularly',
                       'Positive attitude and good sportsmanship are essential'],
      'gender_preference': 'male'
    },
    {
      'event_title': "City Strikers 'football event",
      'sport_type': 'Football',
      'num_players': 3,
      'skill_level_required': 'Advanced',
      'start_time': '24/05/2024 10:00',
      'end_time': '24/05/2024 12:00',
      'location': 'City Stadium, Downtown',
      'description': ['Seeking players with experience in both offense and defense',
                       'Must have excellent communication skills on the field',
                       'Preferably aged between 20-35',
                       'Fitness level must be high to keep up with the intensity of play'],
      'gender_preference': 'female'
    },
    {
      'event_title': "Diamond Kings' baseball event",
      'sport_type': 'Baseball',
      'num_players': 4,
      'skill_level_required': 'Beginner',
      'start_time': '29/05/2024 15:00',
      'end_time': '29/05/2024 17:00',
      'location': 'Diamond Park, Suburbia',
      'description': ['Players of all skill levels welcome, beginners encouraged to join',
                       'Must have own baseball glove and appropriate attire',
                       'Age range between 16-60',
                       'Positive attitude and willingness to learn'],
      'gender_preference': 'mixed'
    }
  ]

  return team_data

# Create the database schema and insert default data
create_event_database()
insert_default_data()

# Test retrieving event data from the database
events = get_event_data()
for event in events:
    print(event)