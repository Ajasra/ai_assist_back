from cocroach_utils.database_utils import conn
from cocroach_utils.db_errors import save_error
from cocroach_utils.db_history import delete_history_by_conv_id


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
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "conv_id": doc[0],
                        "user_id": doc[1],
                        "doc_id": doc[2],
                        "title": doc[3]
                    })
                return docs
        except Exception as err:
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
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM conversations WHERE conv_id = %s",
                    (conversation_id,))
                doc = cur.fetchone()
                return {
                    "conv_id": doc[0],
                    "user_id": doc[1],
                    "doc_id": doc[2],
                    "title": doc[3]
                }
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