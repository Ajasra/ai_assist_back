import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(filename='database.log', level=logging.ERROR)
load_dotenv()
database_url = os.getenv("CR_DATABASE_URL")

# Create a connection pool
db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, database_url)


@contextmanager
def get_db_cursor():
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
        conn.commit()
    except Exception as err:
        conn.rollback()
        logging.error("Failed to get cursor: ", exc_info=True)
    finally:
        db_pool.putconn(conn)


def fetch_all(cursor, query, params=None):
    """
    Fetch all rows from the database
    :param cursor:
    :param query:
    :param params:
    :return:
    """
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchall()

        if result is None:
            return []

        result = [{k: str(v) for k, v in row.items()} for row in result]
        return result

    except Exception as e:
        save_error(e, cursor)
        return []


def fetch_one(cursor, query, params):
    """
    Fetch one row from the database
    :param cursor:
    :param query:
    :param params:
    :return:
    """
    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        if result is None:
            return []
        result = {k: str(v) for k, v in result.items()}
        return result

    except Exception as e:
        save_error(e, cursor)
        return None


def save_error(error, metadata=None):
    """
    Save an error to the database
    :param error:
    :param metadata:
    :return:
    """
    error_message = str(error)
    print(error_message)
    logging.error("An error occurred: ", exc_info=True)
    with get_db_cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO errors (error_text, metadata) VALUES (%s, %s)",
                (error_message, metadata)
            )
        except Exception as e:
            logging.error("Failed to save error to database: ", exc_info=True)

    return -1
