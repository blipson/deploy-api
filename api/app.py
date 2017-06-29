import atexit
from flask import Flask, request
from flask.ext.cors import CORS
from flask_restplus import Api
from functools import wraps

from utils.auth import *
from utils.invalid_usage import *

app = Flask(__name__)
api = Api(app)
CORS(app)

ID_HEADER = 'Authorization'


def up_check():
    return {"status": "happy"}


# Exit Handling
@atexit.register
def exit_handler():
    app.logger.error("Exiting...")


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if ID_HEADER in request.headers:
            token = request.headers[ID_HEADER]
            if valid_token(token) and correct_roles(token):
                return f(*args, **kwargs)
            else:
                return authenticate()
        else:
            return authenticate()

    return decorated


@api.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    return error.to_dict(), error.status_code
