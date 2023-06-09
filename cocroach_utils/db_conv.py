

from cocroach_utils.db_errors import save_error
from cocroach_utils.db_history import delete_history_by_conv_id
from cocroach_utils.database_utils import connect_to_db
from cocroach_utils.db_users import get_user_by_id


def get_all_conversations(user_id):
    """
    Get all conversations for admin
    :return:
    """
    # check if this user has access to this conversation
    user = get_user_by_id(user_id)
    if user is None:
        if user["role"] != 10:
            return []

    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM conversations")
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "conv_id": str(doc[0]),
                        "user_id": str(doc[1]),
                        "doc_id": str(doc[2]),
                        "title": doc[3],
                        "active": doc[4],
                        "summary": doc[5]
                    })
                return docs
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_user_conversations(user_id):
    """
    Get all conversations for the user
    :param user_id:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM conversations WHERE user_id = %s AND active = true",
                    (user_id,))
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "conv_id": str(doc[0]),
                        "user_id": str(doc[1]),
                        "doc_id": str(doc[2]),
                        "title": doc[3],
                        "active": doc[4],
                        "summary": doc[5]
                    })
                return docs
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_conv_by_id(conversation_id):
    """
    Get selected conversation
    :param conversation_id:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM conversations WHERE conv_id = %s",
                    (conversation_id,))
                doc = cur.fetchone()
                return {
                    "conv_id": str(doc[0]),
                    "user_id": str(doc[1]),
                    "doc_id": str(doc[2]),
                    "title": doc[3],
                    "active": doc[4],
                    "summary": doc[5]
                }
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO conversations (user_id, doc_id, title) VALUES (%s, %s, %s) RETURNING conv_id",
                    (user_id, doc_id, title))
                conn.commit()
                return str(cur.fetchone()[0])
        except Exception as err:
            conn.rollback()
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def update_conversation_title(conversation_id, title):
    """
    Update conversation in the database
    :param conversation_id:
    :param title:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET title = %s WHERE conv_id = %s",
                    (title, conversation_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_conversation_summary(conversation_id, summary):
    """
    Update conversation in the database
    :param conversation_id:
    :param summary:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET summary = %s WHERE conv_id = %s",
                    (summary, conversation_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_conversation_active(conversation_id, active = 1):
    """
    Update conversation in the database
    :param conversation_id:
    :param active:
    :return:
    """
    if active == 1:
        active = True
    else:
        active = False

    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET active = %s WHERE conv_id = %s",
                    (active, conversation_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
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
    conn = connect_to_db()
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
            conn.rollback()
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
    # for conv in conversations:
    #     delete_history_by_conv_id(conv[0])

    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM conversations WHERE user_id = %s",
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