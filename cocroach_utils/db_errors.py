import time
import pandas as pd

from cocroach_utils.database_utils import conn


def save_error(error, metadata=None):
    """
    Save the error to the database
    :param metadata:
    :param error:
    :return:
    """
    print(str(error))
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO errors (error_text, metadata, date) VALUES (%s, %s, %s)",
                    (str(error), metadata, pd.Timestamp(time.time(), unit='s')))
                conn.commit()
        except Exception as err:
            print(str(err))
        pass


# ERRORS
def get_errors():
    """
    Get all errors from the database
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM errors")
                return cur.fetchall()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_errors_by_time(start_time, end_time):
    """
    Get all errors from the database
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM errors WHERE date >= %s AND date <= %s",
                    (pd.Timestamp(start_time, unit='s'), pd.Timestamp(end_time, unit='s')))
                return cur.fetchall()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []