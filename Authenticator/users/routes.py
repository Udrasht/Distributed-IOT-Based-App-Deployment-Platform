from flask_restful import Api
from users.views import LoginApi, SignUpApi, InputFileApi


def create_authentication_routes(api: Api):
    """Adds resources to the api.
    :param api: Flask-RESTful Api Object
    """
    api.add_resource(SignUpApi, "/api/auth/register/")
    api.add_resource(LoginApi, "/api/auth/login/")
    api.add_resource(InputFileApi, "/api/upload/file/")