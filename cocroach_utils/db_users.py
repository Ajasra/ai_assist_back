# This file contains all the functions related to the users table in the database
from cocroach_utils.database_utils import connect_to_db, save_error


def get_user_by_id(user_id):
    """
    Get user by id
    :param user_id:
    :return:
    """
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE user_id = %s",
                    (user_id,))
                conn.commit()
                doc = cur.fetchone()
                return {
                    "user_id": str(doc[0]),
                    "name": doc[1],
                    "email": doc[2],
                    "active": doc[4],
                    "role": doc[5],
                }
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_user_password(user_id):
    """
    Get user password by id
    :param user_id:
    :return:
    """
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password FROM users WHERE user_id = %s",
                    (user_id,))
                conn.commit()
                doc = cur.fetchone()
                return doc[0]
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE email = %s",
                    (email,))
                conn.commit()
                doc = cur.fetchone()
                return {
                    "user_id": str(doc[0]),
                    "name": doc[1],
                    "email": doc[2],
                    "password": doc[3],
                    "active": doc[4],
                    "role": doc[5],
                }
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE name = %s",
                    (username,))
                conn.commit()
                doc = cur.fetchone()
                return {
                    "user_id": str(doc[0]),
                    "name": doc[1],
                    "email": doc[2],
                    "password": doc[3],
                    "active": doc[5],
                    "role": doc[6],
                }
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users")
                conn.commit()
                users = []
                for doc in cur.fetchall():
                    users.append({
                        "user_id": str(doc[0]),
                        "name": doc[1],
                        "email": doc[2],
                        "password": doc[3],
                        "active": doc[5],
                    })
                return users
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, email, password, active) VALUES (%s, %s, %s, True) RETURNING user_id",
                    (username, email, password))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET name = %s, email = %s, password = %s WHERE user_id = %s",
                    (username, email, password, user_id))
                conn.commit()
                conn.close()
                return True
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM users WHERE user_id = %s",
                    (user_id,))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_user_field_by_id(user_id, field, value):
    """
    Update user in the database
    :param user_id:
    :param field:
    :param value:
    :return:
    """
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET " + field + " = %s WHERE user_id = %s",
                    (value, user_id))
                conn.commit()
                conn.close()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_user_time(user_id):
    """
    Update user last login time
    :param user_id:
    :return:
    """
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET last_active = NOW() WHERE user_id = %s",
                    (user_id,))
                conn.commit()
                conn.close()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def get_user_tokens(user_id):
    """
    Get user tokens
    :param user_id:
    :return:
    """
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT tokens_used FROM users WHERE user_id = %s", (user_id,))
                conn.commit()
                tokens = []
                result = cur.fetchone()[0]
                # convert string to dict
                tokens = eval(result)
                return tokens
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []