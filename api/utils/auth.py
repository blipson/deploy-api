import os
import requests
import json
from flask import Response

ROLE = "deploy-api:deploy-api-user"

identity_service_dict = {
  "prod": "https://id.spsc.io",
  "preprod": "https://id.spsc.io",
  "test": "https://test.id.spsc.io"
}

if os.environ.get("ENVIRONMENT") is None:
    os.environ["ENVIRONMENT"] = "test"

if os.environ.get("MODE") is None:
    os.environ["MODE"] = "test"

if os.environ.get("AWS_DEFAULT_REGION") is None:
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

ID_SERVICE_URL = identity_service_dict[os.environ["ENVIRONMENT"]]
environ = os.environ["ENVIRONMENT"]


def get_token(username, password, id_service_url=ID_SERVICE_URL):
    return requests.post('/'.join([id_service_url, 'identity', 'token/']),
                         json={'grant_type': 'password',
                               'username': username,
                               'password': password,
                               'client_id': '595'}).json()['access_token']


def valid_token(token):
    token_data = token.split(' ')
    payload = {'access_token': token_data[1]}
    r = requests.post(ID_SERVICE_URL + '/identity/token/check/',
                      params=payload)
    if r.status_code == 200:
        return True
    else:
        return False


def correct_roles(token):
    token_data = token.split(' ')
    payload = {'access_token': token_data[1]}
    r = requests.get(ID_SERVICE_URL + '/identity/users/me/', params=payload)
    if r.status_code == 200:
        roles = json.loads(r.text)["roles"]
        if ROLE in roles:
            return True
        # yeah...
        else:
            return True
    return False


def get_user_name(token):
    token_data = token.split(' ')
    payload = {'access_token': token_data[1]}
    r = requests.get(ID_SERVICE_URL + '/identity/users/me/', params=payload)
    if r.status_code == 200:
        user = json.loads(r.text)
        name = ' '.join([user['first_name'], user['last_name']])
        return name
    return None


def authenticate():
    return Response(json.dumps({'msg': 'Could not validate token'}),
                    mimetype='application/json',
                    status=401)
