from werkzeug.exceptions import HTTPException
from flask import jsonify


class NotAPlate(HTTPException):
    code = 422
    description = "not a valid german plate"


class WrongRequest(HTTPException):
    code = 400
    description = "wrong request"


def handle_err(err):
    return jsonify({"success": False, "error": err.description, "code": err.code}), err.code
