import sqlite3
import os

# This moves the path up one level so it saves in the main 'FastApi' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_NAME = os.path.join(BASE_DIR, "restaurants.db")

def get_connection():
    # check_same_thread=False is required for FastAPI
    return sqlite3.connect(DATABASE_NAME, check_same_thread=False)