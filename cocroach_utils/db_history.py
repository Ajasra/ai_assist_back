import time
import pandas as pd
import psycopg2 as psycopg2

from cocroach_utils.db_errors import save_error
from cocroach_utils.database_utils import connect_to_db


def get_history_for_conv(conversation_id, limit=10):
    """
    Get history for the conversation
    :param conversation_id:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM history WHERE conv_id = %s ORDER BY time DESC LIMIT %s",
                    (conversation_id, limit))
                # format the response into the list of dict with keys
                # hist_id, conv_id, prompt, answer, feedback, time
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "hist_id": doc[0],
                        "conv_id": doc[1],
                        "prompt": doc[2],
                        "answer": doc[3],
                        "time": doc[4],
                        "feedback": doc[5]
                    })
                return docs
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_selected_history(history_id):
    """
    Get selected history
    :param history_id:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM history WHERE hist_id = %s",
                    (history_id,))
                doc = cur.fetchone()
                return {
                    "hist_id": doc[0],
                    "conv_id": doc[1],
                    "prompt": doc[2],
                    "answer": doc[3],
                    "time": doc[4],
                    "feedback": doc[5]
                }
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def add_history(conv_id, prompt, answer, feedback=0):
    """
    Add history to the database and return the new history_id
    :param conv_id:
    :param prompt:
    :param answer:
    :param feedback:
    :return: history_id
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur_time = pd.Timestamp(time.time(), unit='s')
                cur.execute(
                    "INSERT INTO history (conv_id, prompt, answer, feedback, time) VALUES (%s, %s, %s, %s, %s) RETURNING hist_id",
                    (conv_id, prompt, answer, feedback, cur_time))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            conn.rollback()
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def delete_history_by_id(history_id):
    """
    Delete history from the database
    :param history_id:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM history WHERE hist_id = %s",
                    (history_id,))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def delete_history_by_conv_id(conv_id):
    """
    Delete history from the database
    :param conv_id:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM history WHERE conv_id = %s",
                    (conv_id,))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False