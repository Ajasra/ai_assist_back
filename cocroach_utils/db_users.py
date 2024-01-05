# This file contains all the functions related to the users table in the database
from cocroach_utils.database_utils import get_db_cursor, fetch_all, fetch_one


def get_user_by_id(user_id):
    """
    Get user by conv_id
    :param user_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM users WHERE user_id = %s", (user_id,))
    return None


def get_user_by_email(email):
    """
    Get user by email
    :param email:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM users WHERE email = %s", (email,))
    return None


def get_all_users():
    """
    Get all users
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM users")
    return []


def get_user_tokens(user_id):
    """
    Get user tokens
    :param user_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return str(fetch_one(cursor, "SELECT tokens_used FROM users WHERE user_id = %s", (user_id,))['tokens_used'])
    return None


def add_user(username, email, password):
    """
    Add user
    :param username:
    :param email:
    :param password:
    :return:
    """
    # TODO: fix error when user already exist
    with get_db_cursor() as cursor:
        if cursor:
            result = fetch_one(cursor, "INSERT INTO users (name, email, password) "
                                       " VALUES (%s, %s, %s)"
                                       " RETURNING user_id", (username, email, password))
            if result:
                return str(result['user_id'])
            else:
                return -1
    return -1


def update_user(user_id, username, email, password):
    """
    Update user
    :param user_id:
    :param username:
    :param email:
    :param password:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE users SET name = %s, email = %s, password = %s WHERE user_id = %s",
                           (username, email, password, user_id))
            return cursor.rowcount == 1
    return False


def update_user_field(user_id, field, value):
    """
    Update user field
    :param user_id:
    :param field:
    :param value:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE users SET " + field + " = %s WHERE user_id = %s", (value, user_id))
            return cursor.rowcount == 1
    return False


def update_user_time(user_id):
    """
    Update user time
    :param user_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE users SET last_active = NOW() WHERE user_id = %s", (user_id,))
            return cursor.rowcount == 1
    return False


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
