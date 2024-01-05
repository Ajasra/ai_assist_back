import os
import time
from contextlib import contextmanager

import pandas as pd
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
            return conn
        except Exception as e:
            print(str(e))
    else:
        if conn.closed == 1:
            print('Reconnecting to database')
            try:
                conn = psycopg2.connect(database_url)
                return conn
            except Exception as e:
                print(str(e))
        return conn


@contextmanager
def get_db_cursor():
    """
    Get a cursor to the database

    :return:
    """
    connection = connect_to_db()
    if connection is None:
        save_error("No connection to the database")
        yield None
    else:
        try:
            with connection.cursor() as cursor:
                yield cursor
            connection.commit()
        except Exception as err:
            connection.rollback()
            save_error(err)
            yield None
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
    cursor.execute(query, params or ())
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


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
        if cursor.rowcount == 0:
            print("No results found")
            return None
        # i want to fetch one row in dict format (column name: value)
        columns = [col[0] for col in cursor.description]
        result = dict(zip(columns, cursor.fetchone()))
        print(result)
        # result = cursor.fetchone()
        if result:
            return result
        else:
            return None
    except Exception as e:
        save_error(e)
        return None


def save_error(error, metadata=None):
    """
    Save an error to the database
    :param error:
    :param metadata:
    :return:
    """
    print(str(error))
    # with get_db_cursor() as cursor:
    #     if cursor:
    #         print(str(error))
            # return fetch_one(cursor, "INSERT INTO errors (error_text, metadata, date) VALUES (%s, %s, %s)",
            #                  (str(error), metadata, pd.Timestamp(time.time(), unit='s')))
    # return -1
