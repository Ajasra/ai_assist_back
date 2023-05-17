import os
import time

import pandas as pd
import psycopg2 as psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("CR_DATABASE_URL")
conn = None


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


# USERS
def get_user_by_id(user_id):
    """
    Get user by id
    :param user_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE user_id = %s",
                    (user_id,))
                return cur.fetchone()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_user_by_email(email):
    """
    Get user by email
    :param email:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE email = %s",
                    (email,))
                return cur.fetchone()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_user_by_username(username):
    """
    Get user by username
    :param username:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE name = %s",
                    (username,))
                return cur.fetchone()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_all_users():
    """
    Get all users from the database
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users")
                return cur.fetchall()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def add_user(username, email, password):
    """
    Add user to the database and return the new user_id
    :param username:
    :param email:
    :param password:
    :return: user_id
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING user_id",
                    (username, email, password))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def update_user(user_id, username, email, password):
    """
    Update user in the database
    :param user_id:
    :param username:
    :param email:
    :param password:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET name = %s, email = %s, password = %s WHERE user_id = %s",
                    (username, email, password, user_id))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def delete_user(user_id):
    """
    Delete user from the database
    :param user_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM users WHERE user_id = %s",
                    (user_id,))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


# CONVERSATIONS
def get_user_conversations(user_id):
    """
    Get all conversations for the user
    :param user_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM conversations WHERE user_id = %s",
                    (user_id,))
                return cur.fetchall()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_selected_conv(conversation_id):
    """
    Get selected conversation
    :param conversation_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM conversations WHERE conv_id = %s",
                    (conversation_id,))
                return cur.fetchone()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def add_conversation(user_id, doc_id, title="New conversation"):
    """
    Add conversation to the database and return the new conv_id
    :param user_id:
    :param doc_id:
    :param title:
    :return: conv_id
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO conversations (user_id, doc_id, title) VALUES (%s, %s, %s) RETURNING conv_id",
                    (user_id, doc_id, title))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def update_conversation(conversation_id, title):
    """
    Update conversation in the database
    :param conversation_id:
    :param title:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET title = %s WHERE conv_id = %s",
                    (title, conversation_id))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def delete_conversation(conversation_id):
    """
    Delete conversation from the database
    :param conversation_id:
    :return:
    """
    if conn is not None:
        try:
            delete_history_by_conv_id(conversation_id)
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM conversations WHERE conv_id = %s",
                    (conversation_id,))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def delete_conversation_by_user(user_id):
    """
    Delete conversation from the database
    :param user_id:
    :return:
    """
    # get all conversations for the user
    conversations = get_user_conversations(user_id)
    for conv in conversations:
        delete_history_by_conv_id(conv[0])

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM conversations WHERE user_id = %s",
                    (user_id,))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


# HISTORY
def get_history_for_conv(conversation_id):
    """
    Get history for the conversation
    :param conversation_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM history WHERE conv_id = %s",
                    (conversation_id,))
                return cur.fetchall()
        except Exception as err:
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
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur_time = time.time()
                cur.execute(
                    "INSERT INTO history (conv_id, prompt, answer, feedback, time) VALUES (%s, %s, %s, %s, %s) RETURNING hist_id",
                    (conv_id, prompt, answer, feedback, cur_time))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def get_selected_history(history_id):
    """
    Get selected history
    :param history_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM history WHERE hist_id = %s",
                    (history_id,))
                return cur.fetchone()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def delete_history_by_id(history_id):
    """
    Delete history from the database
    :param history_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM history WHERE hist_id = %s",
                    (history_id,))
                conn.commit()
                return True
        except Exception as err:
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
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM history WHERE conv_id = %s",
                    (conv_id,))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


# DOCS
def get_user_docs(user_id):
    """
    Get all docs for the user
    :param user_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents WHERE user_id = %s",
                    (user_id,))
                return cur.fetchall()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_doc_by_id(doc_id):
    """
    Get doc by id
    :param doc_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents WHERE doc_id = %s",
                    (doc_id,))
                return cur.fetchone()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_all_docs():
    """
    Get all docs
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents")
                return cur.fetchall()
        except Exception as err:
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def add_doc(user_id, doc_name, doc_text):
    """
    Add doc to the database and return the new doc_id
    :param user_id:
    :param doc_name:
    :param doc_text:
    :return: doc_id
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO documents (user_id, name, summary, updated) VALUES (%s, %s, %s, %s) RETURNING doc_id",
                    (user_id, doc_name, doc_text, pd.Timestamp(time.time(), unit='s')))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def delete_doc_by_id(doc_id):
    """
    Delete doc from the database
    :param doc_id:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM documents WHERE doc_id = %s",
                    (doc_id,))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_doc_summary_by_id(doc_id, doc_text):
    """
    Update doc summary
    :param doc_id:
    :param doc_text:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE documents SET summary = %s, updated = %s WHERE doc_id = %s",
                    (doc_text, pd.Timestamp(time.time(), unit='s'), doc_id))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_doc_name_by_id(doc_id, doc_name):
    """
    Update doc name
    :param doc_id:
    :param doc_name:
    :return:
    """
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE documents SET name = %s, updated = %s WHERE doc_id = %s",
                    (doc_name, pd.Timestamp(time.time(), unit='s'), doc_id))
                conn.commit()
                return True
        except Exception as err:
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


try:
    conn = psycopg2.connect(database_url)
except Exception as e:
    save_error(e)
