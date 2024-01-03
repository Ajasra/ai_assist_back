# This file contains all the functions for the conversations table
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
                # add to below also assistant.title from assistants table by conversations.assistant
                cur.execute(
                    "SELECT conv_id, user_id, doc_id, conversations.title, active, summary, models.name, "
                    "assistants.title FROM conversations LEFT JOIN models ON conversations.model = models._id LEFT "
                    "JOIN assistants ON conversations.assistant = assistants._id",
                    (user_id,))
                conn.commit()
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "conv_id": str(doc[0]),
                        "user_id": str(doc[1]),
                        "doc_id": str(doc[2]),
                        "title": doc[3],
                        "active": doc[4],
                        "summary": doc[5],
                        "model": doc[6],
                        "assistant": doc[7]
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
                    "SELECT conv_id, user_id, doc_id, conversations.title, active, summary, models.name, "
                    "assistants.title, assistants.system_prompt FROM conversations LEFT JOIN models ON conversations.model = models._id LEFT "
                    "JOIN assistants ON conversations.assistant = assistants._id "
                    "WHERE conversations.user_id = %s",
                    (user_id,))
                conn.commit()
                docs = []
                for doc in cur.fetchall():
                    docs.append({
                        "conv_id": str(doc[0]),
                        "user_id": str(doc[1]),
                        "doc_id": str(doc[2]),
                        "title": doc[3],
                        "active": doc[4],
                        "summary": doc[5],
                        "model": doc[6],
                        "assistant": doc[7],
                        "system_prompt": doc[8]
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
                    "SELECT conv_id, user_id, doc_id, conversations.title, active, summary, models.name, "
                    "assistants.title, assistants.system_prompt FROM conversations LEFT JOIN models ON conversations.model = models._id LEFT "
                    "JOIN assistants ON conversations.assistant = assistants._id "
                    "WHERE conv_id = %s",
                    (conversation_id,))
                conn.commit()
                doc = cur.fetchone()
                return {
                    "conv_id": str(doc[0]),
                    "user_id": str(doc[1]),
                    "doc_id": str(doc[2]),
                    "title": doc[3],
                    "active": doc[4],
                    "summary": doc[5],
                    "model": doc[6],
                    "assistant": doc[7],
                    "system_prompt": doc[8]
                }
        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def add_conversation(user_id, doc_id=None, title="New conversation", model=0, assistant=0):
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
                    "INSERT INTO conversations (user_id, doc_id, title, model, assistant) VALUES (%s, %s, %s, %s, %s) RETURNING conv_id",
                    (user_id, doc_id, title, model, assistant))
                conn.commit()
                return str(cur.fetchone()[0])
        except Exception as err:
            conn.rollback()
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def update_conversation_field(conversation_id, field, value):
    """
    Update conversation in the database
    :param conversation_id:
    :param field:
    :param value:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET " + field + " = %s WHERE conv_id = %s",
                    (value, conversation_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


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


def update_conversation_model(conversation_id, model):
    """
    Update conversation in the database
    :param conversation_id:
    :param model:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET model = %s WHERE conv_id = %s",
                    (model, conversation_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def update_conversation_assistant(conversation_id, assistant):
    """
    Update conversation in the database
    :param conversation_id:
    :param assistant:
    :return:
    """
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE conversations SET assistant = %s WHERE conv_id = %s",
                    (assistant, conversation_id))
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