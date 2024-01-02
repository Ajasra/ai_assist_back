from cocroach_utils.database_utils import connect_to_db
from cocroach_utils.db_errors import save_error


def get_all_assistants():
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM assistants")
                rows = cur.fetchall()
                return rows

        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_assistant_by_id(assistant_id):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM assistants WHERE _id = %s",
                    (assistant_id,))
                row = cur.fetchone()
                return row

        except Exception as err:
            conn.rollback()
            save_error(err)
            return None
    else:
        save_error("No connection to the database")
        return None


def get_assistant_by_name(assistant_name):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM assistants WHERE title = %s",
                    (assistant_name,))
                row = cur.fetchone()
                return row

        except Exception as err:
            conn.rollback()
            save_error(err)
            return None
    else:
        save_error("No connection to the database")
        return None


def get_assistant_by_user(user_id):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM assistants WHERE user = %s",
                    (user_id,))
                row = cur.fetchone()
                return row

        except Exception as err:
            conn.rollback()
            save_error(err)
            return None
    else:
        save_error("No connection to the database")
        return None


def add_assistant(title, description ="", welcome_message = "", system_prompt = "", user = 0):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO assistants (title, description, welcome_msg, system_prompt, user) VALUES (%s, %s, %s, %s, %s)",
                    (title, description, welcome_message, system_prompt, user))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            conn.rollback()
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def update_assistant(title, description, welcome_message, system_prompt, user):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE assistants SET title = %s, description = %s, welcome_msg = %s, system_prompt = %s WHERE user = %s",
                    (title, description, welcome_message, system_prompt, user))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def delete_assistant(assistant_id):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM assistants WHERE _id = %s",
                    (assistant_id,))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False