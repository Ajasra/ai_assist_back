# Description: Database functions for documents
import time
import pandas as pd

from cocroach_utils.database_utils import get_db_cursor, fetch_all, fetch_one


def get_user_docs(user_id):
    """
    Get all docs for the user
    :param user_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM documents WHERE user_id = %s AND active = true", (user_id,))
    return []


def get_doc_by_id(doc_id):
    """
    Get doc by conv_id
    :param doc_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM documents WHERE doc_id = %s", (doc_id,))
    return None


def get_all_docs():
    """
    Get all docs
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM documents")
    return []


def get_doc_by_name(doc_name):
    """
    Get doc by name
    :param doc_name:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM documents WHERE name = %s", (doc_name,))
    return None


def add_doc(user_id, doc_name, doc_text):
    """
    Add doc to the database and return the new doc_id
    :param user_id:
    :param doc_name:
    :param doc_text:
    :return: doc_id
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "INSERT INTO documents (user_id, name, summary, updated) VALUES (%s, %s, %s, %s) "
                                     "RETURNING doc_id",
                             (user_id, doc_name, doc_text, pd.Timestamp(time.time(), unit='s')))['doc_id']
    return -1


def update_doc_field_by_id(doc_id, field, value):
    """
    Update doc fields
    :param doc_id:
    :param field:
    :param value:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE documents SET " + field + " = %s, updated = %s WHERE doc_id = %s",
                           (value, pd.Timestamp(time.time(), unit='s'), doc_id))
            return cursor.rowcount == 1
    return False


def delete_doc_by_id(doc_id):
    """
    Delete doc from the database
    :param doc_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE documents SET active = %s WHERE doc_id = %s", (False, doc_id,))
            return cursor.rowcount == 1
    return False
