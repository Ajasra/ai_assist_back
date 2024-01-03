from cocroach_utils.database_utils import connect_to_db
from cocroach_utils.db_errors import save_error


def get_all_models():
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM models")
                models = []
                for model in cur.fetchall():
                    models.append({
                        "id": model[0],
                        "name": model[1],
                        "description": model[2],
                        "price_in": model[3],
                        "price_out": model[4]
                    })
                return models

        except Exception as err:
            conn.rollback()
            save_error(err)
            return []
    else:
        save_error("No connection to the database")
        return []


def get_model_by_id(model_id):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM models WHERE _id = %s",
                    (model_id,))
                row = cur.fetchone()
                return {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price_in": row[3],
                    "price_out": row[4]
                }

        except Exception as err:
            conn.rollback()
            save_error(err)
            return None
    else:
        save_error("No connection to the database")
        return None


def get_model_by_name(model_name):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM models WHERE name = %s",
                    (model_name,))
                row = cur.fetchone()
                return row

        except Exception as err:
            conn.rollback()
            save_error(err)
            return None
    else:
        save_error("No connection to the database")
        return None


def add_model(name, description="", price_in=0.0, price_out=0.0):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO models (name, description, price_in, price_out) VALUES (%s, %s, %s, %s)",
                    (name, description, price_in, price_out))
                conn.commit()
                return str(cur.fetchone()[0])
        except Exception as err:
            conn.rollback()
            save_error(err)
            return -1
    else:
        save_error("No connection to the database")
        return -1


def update_model(model_id, name, description="", price_in=0.0, price_out=0.0):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE models SET name = %s, description = %s, price_in = %s, price_out = %s WHERE _id = %s",
                    (name, description, price_in, price_out, model_id))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False


def delete_model(model_id):
    conn = connect_to_db()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM models WHERE _id = %s",
                    (model_id,))
                conn.commit()
                return True
        except Exception as err:
            conn.rollback()
            save_error(err)
            return False
    else:
        save_error("No connection to the database")
        return False
