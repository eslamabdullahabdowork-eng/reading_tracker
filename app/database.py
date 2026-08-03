import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            database="reading_tracker",
            user="postgres",
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port="5432"
        )