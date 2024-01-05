from cocroach_utils.database_utils import get_db_cursor, fetch_all, fetch_one


def get_all_assistants():
    """
    Get all assistants
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM assistants")
    return []


def get_assistant_by_id(assistant_id):
    """
    Get assistant by conv_id
    :param assistant_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM assistants WHERE assist_id = %s", (assistant_id,))
    return None


def get_assistant_by_name(assistant_name):
    """
    Get assistant by name
    :param assistant_name:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM assistants WHERE name = %s", (assistant_name,))
    return None


def get_assistant_by_user(user_id):
    """
    Get assistant by user
    :param user_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM assistants WHERE user_id = %s", (user_id,))
    return None


def add_assistant(title, description="", welcome_message="", system_prompt="", user=0):
    """
    Add assistant
    :param title:
    :param description:
    :param welcome_message:
    :param system_prompt:
    :param user:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor,
                             "INSERT INTO assistants (name, description, welcome, system_prompt, user_id) VALUES (%s, "
                             "%s, %s, %s, %s) RETURNING assist_id",
                             (title, description, welcome_message, system_prompt, user))['assist_id']
    return -1


def update_assistant(assistant_id, title, description, welcome_message, system_prompt, user):
    """
    Update assistant
    :param assistant_id:
    :param title:
    :param description:
    :param welcome_message:
    :param system_prompt:
    :param user:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute(
                "UPDATE assistants SET name = %s, description = %s, welcome = %s, system_prompt = %s, user_id = %s "
                "WHERE assist_id = %s",
                (title, description, welcome_message, system_prompt, user, assistant_id))
            return cursor.rowcount == 1
    return False


def update_assistant_field(assistant_id, field, value):
    """
    Update assistant field
    :param assistant_id:
    :param field:
    :param value:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE assistants SET " + field + " = %s WHERE _id = %s",
                           (value, assistant_id))
            return cursor.rowcount == 1
    return False


def delete_assistant(assistant_id):
    """
    Delete assistant
    :param assistant_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM assistants WHERE assist_id = %s", (assistant_id,))
            return cursor.rowcount == 1
    return False
