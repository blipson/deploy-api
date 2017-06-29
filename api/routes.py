import json
from json import JSONDecodeError

import requests
from flask_restplus import Resource, fields
from flask import request

from app import app, api, requires_auth
from app import up_check

from utils.invalid_usage import InvalidUsage

response_model = api.model("response_model", {})

ID_HEADER = 'Authorization'


@api.route("/up")
class Up(Resource):
    def get(self):
        result = up_check()
        return result


@api.route("/test")
class Test(Resource):
    @api.header("Authorization", "identity service token", required=True)
    @api.response(200, "success", response_model)
    @requires_auth
    def post(self):
        body = request.data.decode("utf-8")
        token = request.headers[ID_HEADER]
        status = "idunno"
        try:
            body = json.loads(body)
            for test in body:
                res = requests.get(test["url"])
                res_json = json.loads(res.text)
                if res_json == test["expected_output"]:
                    status = "success"
                else:
                    status = "failure"
        except JSONDecodeError as e:
            app.logger.error(e)
            raise InvalidUsage(str(e), status_code=400)
        return {
            "status": status
        }
