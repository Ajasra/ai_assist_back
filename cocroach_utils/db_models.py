from cocroach_utils.database_utils import get_db_cursor, fetch_all, fetch_one


def get_all_models():
    """
    Get all models
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM models")
    return []


def get_model_by_id(model_id):
    """
    Get model by conv_id
    :param model_id:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM models WHERE model_id = %s", (model_id,))
    return None


def get_model_by_name(model_name):
    """
    Get model by name
    :param model_name:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM models WHERE name = %s", (model_name,))
    return None


def add_model(name, description="", price_in=0.0, price_out=0.0):
    """
    Add a new model
    :param name:
    :param description:
    :param price_in:
    :param price_out:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("INSERT INTO models (name, description, price_in, price_out) VALUES (%s, %s, %s, "
                           "%s)", (name, description, price_in, price_out))
            return cursor.rowcount == 1
    return False


def update_model(model_id, name, description="", price_in=0.0, price_out=0.0):
    """
    Update a model
    :param model_id:
    :param name:
    :param description:
    :param price_in:
    :param price_out:
    :return:
    """
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("UPDATE models SET name = %s, description = %s, price_in = %s, price_out = %s "
                           "WHERE model_id = %s", (name, description, price_in, price_out, model_id))
            return cursor.rowcount == 1
    return False


def delete_model(model_id):
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM models WHERE model_id = %s", (model_id,))
            return cursor.rowcount == 1
    return False
