import sqlite3
import contextlib
from pathlib import Path

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
            age INTEGER NOT NULL,
            preferredlocation TEXT NOT NULL,
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

