# This file contains all the functions for the conversations table
from cocroach_utils.db_history import delete_history_by_conv_id
from cocroach_utils.database_utils import connect_to_db, save_error, get_db_cursor, fetch_all, fetch_one
from cocroach_utils.db_users import get_user_by_id


def get_all_docs():
    """
    Get all docs
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM documents")
    return []


def get_all_conversations_by_user(user_id):
    """
    Get all conversations for admin
    :param user_id:
    :return:
    """
    user = get_user_by_id(user_id)
    if user is None:
        if user["role"] != 10:
            return []

    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor,
                             "SELECT conv_id, user_id, doc_id, conversations.title, active, summary, models.name, "
                             "assistants.title, memory FROM conversations "
                             "LEFT JOIN models ON conversations.model = models._id LEFT "
                             "JOIN assistants ON conversations.assistant = assistants._id", (user_id,))
    return []


def get_user_conversations(user_id):
    """
    Get all conversations for the user
    :param user_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor,
                             "SELECT conv_id, user_id, doc_id, conversations.title, active, summary, models.name, "
                             "assistants.title, assistants.system_prompt, memory FROM conversations "
                             "LEFT JOIN models ON conversations.model = models._id LEFT "
                             "JOIN assistants ON conversations.assistant = assistants._id "
                             "WHERE conversations.user_id = %s", (user_id,))
    return []


def get_conv_by_id(conversation_id):
    """
    Get selected conversation
    :param conversation_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor,
                             "SELECT conv_id, user_id, doc_id, conversations.title, active, summary, models.name, "
                             "assistants.title, assistants.system_prompt, memory FROM conversations "
                             "LEFT JOIN models ON conversations.model = models._id LEFT "
                             "JOIN assistants ON conversations.assistant = assistants._id "
                             "WHERE conv_id = %s", (conversation_id,))
    return []


def add_conversation(user_id, doc_id=None, title="New conversation", model=0, assistant=0):
    """
    Add conversation to the database and return the new conv_id
    :param assistant:
    :param model:
    :param user_id:
    :param doc_id:
    :param title:
    :return: conv_id
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor,
                             "INSERT INTO conversations (user_id, doc_id, title, model, assistant) VALUES (%s, %s, %s, "
                             "%s, %s) RETURNING conv_id", (user_id, doc_id, title, model, assistant))['conv_id']
    return -1


def update_conversation_field(conversation_id, field, value):
    """
    Update conversation in the database
    :param conversation_id:
    :param field:
    :param value:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE conversations SET " + field + " = %s WHERE conv_id = %s",
                           (value, conversation_id))
            return cursor.rowcount == 1
    return False


def delete_conversation(conversation_id):
    """
    Delete conversation from the database
    :param conversation_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM conversations WHERE conv_id = %s", (conversation_id,))
            return cursor.rowcount == 1
    return False


def delete_conversation_by_user(user_id, delete_history=False):
    """
    Delete conversation from the database
    :param delete_history:
    :param user_id:
    :return:
    """

    if delete_history:
        # get all conversations for the user
        conversations = get_user_conversations(user_id)
        for conv in conversations:
            delete_history_by_conv_id(conv[0])

    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM conversations WHERE user_id = %s", (user_id,))
            return cursor.rowcount == 1
    return False

