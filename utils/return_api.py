import os

local_key = os.getenv("PUBLIC_API_KEY")


def check_api_key(api_key):
    """
    Check access
    :param api_key:
    :return:
    """
    if api_key is None:
        return False
    if api_key == local_key:
        return True
    return False


def return_error(err_code, err_message):
    """
    Return error message
    :param err_code:
    :param err_message:
    :return:
    """
    return {
        "response": err_message,
        "code": err_code,
        "status": "error"
    }


def return_success(data):
    """
    Return data
    :param data:
    :return:
    """
    return {
        "response": data,
        "code": 200,
        "status": "success"
    }


def wrong_api():
    """
    Return message on wrong api
    :return:
    """
    return return_error(400, "Invalid API Key")


def check_result(result, err_code, err_msg):
    """
    Check result
    :param result:
    :param err_code:
    :param err_msg:
    :return:
    """
    if result == [] or result == -1 or result is None or not result:
        return return_error(err_code, err_msg)
    return return_success(result)