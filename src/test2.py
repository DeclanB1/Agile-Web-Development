import sqlite3
from create_database import get_event_data

events = get_event_data()
for event in events:
    print(event)

# def get_user_data():
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()

#     # Retrieve all events from the database
#     c.execute('SELECT * FROM users')
#     events = c.fetchall()

#     conn.close()

#     return events

# users = get_user_data()
# for user in users:
#     print(user)


