import shutil
import time
import pandas as pd

from cocroach_utils.db_errors import save_error

from cocroach_utils.database_utils import connect_to_db


# GET
def get_user_docs(user_id):
    """
    Get all docs for the user
    :param user_id:
    :return:
    """
    conn = connect_to_db()

    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents WHERE user_id = %s AND active = true",
                    (user_id,))
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "doc_id": str(doc[0]),
                        "name": doc[1],
                        "summary": doc[2],
                        "user_id": str(doc[3]),
                        "updated": doc[4]
                    })
                return docs
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents WHERE doc_id = %s",
                    (doc_id,))
                doc = cur.fetchone()
                return {
                    "doc_id": str(doc[0]),
                    "name": doc[1],
                    "summary": doc[2],
                    "user_id": str(doc[3]),
                    "updated": doc[4]
                }
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents")
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "doc_id": str(doc[0]),
                        "name": doc[1],
                        "summary": doc[2],
                        "user_id": str(doc[3]),
                        "updated": doc[4]
                    })
                return docs
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_doc_by_name(doc_name):
    """
    Get doc by name
    :param doc_name:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents WHERE name = %s",
                    (doc_name,))
                doc = cur.fetchone()
                return {
                        "doc_id": str(doc[0]),
                        "name": doc[1],
                        "summary": doc[2],
                        "user_id": str(doc[3]),
                        "updated": doc[4]
                    }
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []



# ADD
def add_doc(user_id, doc_name, doc_text):
    """
    Add doc to the database and return the new doc_id
    :param user_id:
    :param doc_name:
    :param doc_text:
    :return: doc_id
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO documents (user_id, name, summary, updated) VALUES (%s, %s, %s, %s) RETURNING doc_id",
                    (user_id, doc_name, doc_text, pd.Timestamp(time.time(), unit='s')))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as err:
            conn.rollback()
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


# UPDATE
def update_doc_summary_by_id(doc_id, doc_text):
    """
    Update doc summary
    :param doc_id:
    :param doc_text:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE documents SET summary = %s, updated = %s WHERE doc_id = %s",
                    (doc_text, pd.Timestamp(time.time(), unit='s'),  doc_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_doc_steps_by_id(doc_id, steps):
    """
    Update doc summary
    :param doc_id:
    :param doc_text:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE documents SET updated = %s, summary_steps = %s WHERE doc_id = %s",
                    ( pd.Timestamp(time.time(), unit='s'), steps, doc_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE documents SET name = %s, updated = %s WHERE doc_id = %s",
                    (doc_name, pd.Timestamp(time.time(), unit='s'), doc_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


# DELETE
def delete_doc_by_id(doc_id):
    """
    Delete doc from the database
    :param doc_id:
    :return:
    """
    conn = connect_to_db()

    print("delete_doc_by_id", doc_id    )
    if conn is not None:
        try:
            with conn.cursor() as cur:
                # cur.execute(
                #     "DELETE FROM documents WHERE doc_id = %s",
                #     (doc_id,))
                cur.execute(
                    "UPDATE documents SET active = %s WHERE doc_id = %s",
                    (False, doc_id))
                conn.commit()
                # delete folder and all files in it from the server './db/doc_id'
                # shutil.rmtree('./db/' + str(doc_id))
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False