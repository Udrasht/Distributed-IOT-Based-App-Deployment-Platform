from flask import Response
from flask_restful import Resource
from flask import request, make_response
from users.service import create_user, login_user, validate_json


class SignUpApi(Resource):
    @staticmethod
    def post() -> Response:
        """
        POST response method for creating user.

        :return: JSON object
        """
        input_data = request.get_json()
        response, status = create_user(request, input_data)
        return make_response(response, status)

class LoginApi(Resource):
    @staticmethod
    def post() -> Response:
        """
        POST response method for login user.

        :return: JSON object
        """
        input_data = request.get_json()
        response, status = login_user(request, input_data)
        return make_response(response, status)

class InputFileApi(Resource):
    @staticmethod
    def post() -> Response:
        """
        POST response method for taking a json file
        :return: JSON object
        """
        inpFile = request.files['inpFile']
        response, status = validate_json(request, inpFile)
        return make_response(response, status)