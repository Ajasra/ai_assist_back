from cocroach_utils.database_utils import conn
from cocroach_utils.db_errors import save_error


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
                doc = cur.fetchone()
                return {
                    "user_id": str(doc[0]),
                    "name": doc[1],
                    "email": doc[2],
                    "active": doc[4],
                }
        except Exception as err:
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
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password FROM users WHERE user_id = %s",
                    (user_id,))
                doc = cur.fetchone()
                return doc[0]
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
                doc = cur.fetchone()
                print(doc)
                return {
                    "user_id": str(doc[0]),
                    "name": doc[1],
                    "email": doc[2],
                    "password": doc[3],
                    "active": doc[4],
                }
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
                doc = cur.fetchone()
                return {
                    "user_id": str(doc[0]),
                    "name": doc[1],
                    "email": doc[2],
                    "password": doc[3],
                    "active": doc[5],
                }
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
                    "INSERT INTO users (name, email, password, active) VALUES (%s, %s, %s, True) RETURNING user_id",
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
