import os
import time
from contextlib import contextmanager

import pandas as pd
import psycopg2 as psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()
database_url = os.getenv("CR_DATABASE_URL")
conn = None


def connect_to_db():
    """
    Connect to the database
    :return:
    """
    global conn

    if conn is None or conn.closed == 1:
        try:
            conn = psycopg2.connect(database_url)
        except Exception as e:
            raise Exception("Failed to connect to the database: " + str(e))

    return conn


@contextmanager
def get_db_cursor():
    """
    Get a cursor to the database

    :return:
    """
    connection = connect_to_db()
    if connection is None:
        raise Exception("No connection to the database")
    else:
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor
            connection.commit()
        except Exception as err:
            connection.rollback()
            raise Exception("Failed to get cursor: " + str(err))
        finally:
            connection.close()


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


def save_error(error, metadata=None, cursor=None):
    """
    Save an error to the database
    :param cursor:
    :param error:
    :param metadata:
    :return:
    """

    print(str(error))

    # if cursor is None:
    #     with get_db_cursor() as cursor:
    #         if cursor:
    #             return fetch_one(cursor, "INSERT INTO errors (error_text, metadata, date) VALUES (%s, %s, %s)",
    #                              (str(error), metadata, pd.Timestamp(time.time(), unit='s')))
    # else:
    #     if cursor:
    #         return fetch_one(cursor, "INSERT INTO errors (error_text, metadata, date) VALUES (%s, %s, %s)",
    #                          (str(error), metadata, pd.Timestamp(time.time(), unit='s')))
    return -1
