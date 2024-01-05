# This file contains all the functions related to the conversation history table in the database
import time
import pandas as pd

from cocroach_utils.database_utils import get_db_cursor, fetch_all, fetch_one


def delete_user(user_id):
    """
    Delete user
    :param user_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            return cursor.rowcount == 1
    return False


def get_history_for_conv(conversation_id, limit=10):
    """
    Get history for conversation
    :param conversation_id:
    :param limit:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM history WHERE conv_id = %s ORDER BY time DESC LIMIT %s",
                             (conversation_id, limit))
    return []


def get_selected_history(history_id):
    """
    Get selected history
    :param history_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM history WHERE hist_id = %s", (history_id,))
    return []


def add_history(conv_id, prompt, answer, followup=None, feedback=0):
    """
    Add history
    :param conv_id:
    :param prompt:
    :param answer:
    :param followup:
    :param feedback:
    :return:
    """
    if followup is None:
        followup = ''

    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "INSERT INTO history (conv_id, prompt, answer, feedback, time, followup) VALUES "
                                     "(%s, %s, %s, %s, %s, %s) RETURNING hist_id",
                             (conv_id, prompt, answer, feedback, pd.Timestamp(time.time(), unit='s'), followup))['hist_id']
    return -1


def update_history_field_by_id(history_id, field, value):
    """
    Update history field by id
    :param history_id:
    :param field:
    :param value:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE history SET " + field + " = %s WHERE hist_id = %s",
                           (value, history_id))
            return cursor.rowcount == 1
    return False


def delete_history_by_id(history_id):
    """
    Delete history by id
    :param history_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM history WHERE hist_id = %s", (history_id,))
            return cursor.rowcount == 1
    return False


def delete_history_by_conv_id(conv_id):
    """
    Delete history by conversation id
    :param conv_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM history WHERE conv_id = %s", (conv_id,))
            return cursor.rowcount == 1
    return False
