import json
import logging
from flask import Response, request
from werkzeug.exceptions import HTTPException, BadRequest, NotFound, InternalServerError
from typing import Union

HTTPError = Union[BadRequest, HTTPException, NotFound, InternalServerError]


class ServerError(InternalServerError):
    name = ""
    description = ""


def failure(exception: HTTPError):
    response = Response(response=json.dumps({
        "code": exception.code,
        "name": exception.name,
        "description": exception.description
    }),
        headers={"Content-Type": "application/json"},
        status=exception.code)
    return response


def request_logger(requests: request) -> None:
    application_id = requests.headers.get('X-Application-Id', 'Unknown Source')
    logging.info(f'Incoming requests from: {application_id}')
