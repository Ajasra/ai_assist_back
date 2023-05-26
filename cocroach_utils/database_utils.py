import os
import psycopg2 as psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("CR_DATABASE_URL")
conn = None


def connect_to_db():
    """
    Connect to the database
    :return:
    """
    global conn
    if conn is None:
        try:
            conn = psycopg2.connect(database_url)
        except Exception as e:
            print(str(e))


connect_to_db()


