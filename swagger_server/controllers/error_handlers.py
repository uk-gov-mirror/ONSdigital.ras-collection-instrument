from flask import jsonify, make_response


def request_exception_handler(error):
    return make_response(jsonify(error.message), error.status_code)
