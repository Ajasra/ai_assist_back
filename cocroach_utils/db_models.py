from cocroach_utils.database_utils import get_db_cursor, fetch_all, fetch_one


def get_all_models():
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_all(cursor, "SELECT * FROM models")
    return []


def get_model_by_id(model_id):
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM models WHERE _id = %s", (model_id,))
    return None


def get_model_by_name(model_name):
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "SELECT * FROM models WHERE name = %s", (model_name,))
    return None


def add_model(name, description="", price_in=0.0, price_out=0.0):
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "INSERT INTO models (name, description, price_in, price_out) VALUES (%s, %s, %s, "
                                     "%s)", (name, description, price_in, price_out))[0]
    return -1


def update_model(model_id, name, description="", price_in=0.0, price_out=0.0):
    with get_db_cursor() as cursor:
        if cursor:
            return fetch_one(cursor, "UPDATE models SET name = %s, description = %s, price_in = %s, price_out = %s "
                                     "WHERE _id = %s", (name, description, price_in, price_out, model_id))[0]
    return False


def delete_model(model_id):
    with get_db_cursor() as cursor:
        if cursor:
            cursor.execute("DELETE FROM models WHERE _id = %s", (model_id,))
            return cursor.rowcount == 1
    return False
