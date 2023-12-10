import json
import jwt
import datetime
from server import db
from os import environ, path
from users.models import User
from flask_bcrypt import generate_password_hash
from utils.common import generate_response, TokenGenerator
from users.validation import (
    CreateLoginInputSchema,
    CreateSignupInputSchema
)
from utils.http_code import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from werkzeug.utils import secure_filename
import json, random, string
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def create_user(request, input_data):
    """
    It creates a new user

    :param request: The request object
    :param input_data: This is the data that is passed to the function
    :return: A response object
    """
    create_validation_schema = CreateSignupInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)
    check_username_exist = User.query.filter_by(
        username=input_data.get("username")
    ).first()
    check_email_exist = User.query.filter_by(email=input_data.get("email")).first()
    if check_username_exist:
        return generate_response(
            message="Username already exist", status=HTTP_400_BAD_REQUEST
        )
    elif check_email_exist:
        return generate_response(
            message="Email  already taken", status=HTTP_400_BAD_REQUEST
        )

    new_user = User(**input_data)  # Create an instance of the User class
    new_user.hash_password()
    db.session.add(new_user)  # Adds new User record to database
    db.session.commit()  # Comment
    del input_data["password"]
    return generate_response(
        data=input_data, message="User Created", status=HTTP_201_CREATED
    )


def login_user(request, input_data):
    """
    It takes in a request and input data, validates the input data, checks if the user exists, checks if
    the password is correct, and returns a response

    :param request: The request object
    :param input_data: The data that is passed to the function
    :return: A dictionary with the keys: data, message, status
    """
    create_validation_schema = CreateLoginInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)

    get_user = User.query.filter_by(email=input_data.get("email")).first()
    print(get_user.username)
    if get_user is None:
        return generate_response(message="User not found", status=HTTP_400_BAD_REQUEST)
    if get_user.check_password(input_data.get("password")):
        token = jwt.encode(
            {
                "id": get_user.id,
                "email": get_user.email,
                "username": get_user.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            environ.get("SECRET_KEY"),
        )
        input_data["token"] = token
        input_data["username"] = get_user.username
        del input_data["password"]
        return generate_response(
            data=input_data, message="User login successfully", status=HTTP_201_CREATED
        )
    else:
        return generate_response(
            message="Password is wrong", status=HTTP_400_BAD_REQUEST
        )

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def upload_file(inpFile, fileName, filePath):
    connect_str = environ.get('AZURE_CONN_STRING')
    fileStorageContainer = environ.get('STORAGE_CONTAINER')

    # Create a BlobServiceClient object using the connection string
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    fileextension = fileName.rsplit('.',1)[1]
    Randomfilename = id_generator()
    fileName = Randomfilename + '.' + fileextension
    blob_name = fileName
    print(blob_name)
    print(filePath)
    # Create a ContainerClient object for the container
    container_client = blob_service_client.get_container_client(fileStorageContainer)

    # Upload the file to the container
    with open(filePath, "rb") as data:
        try:
            container_client.upload_blob(blob_name, data)
        except Exception as e:
            print(e)



    # fileStorageAcc = environ.get('STORAGE_ACC')
    # fileStorageKey = environ.get('STORAGE_KEY')
    # fileextension = fileName.rsplit('.',1)[1]
    # Randomfilename = id_generator()
    # fileName = Randomfilename + '.' + fileextension
    # blob_service = BlobServiceClient(account_name=fileStorageAcc, account_key=fileStorageKey)
    # try:
    #     blob_service.create_blob_from_stream(fileStorageContainer, fileName, inpFile)
    # except Exception:
    #     print('Exception=' + Exception)
    #     pass


def validate_json(request, inpFile):
    if inpFile:
        fileName = secure_filename(inpFile.filename)
        basedir = path.abspath(path.dirname(__file__))
        filePath = path.join(basedir, "..", "static", "uploads", fileName)
        inpFile.save(filePath)
        with open(filePath) as file:
            try:
                data = json.load(file)
            except Exception as e:
                return generate_response(
                    data=str(e),
                    message=str(e),
                    status=HTTP_400_BAD_REQUEST
                )
            else:
                expected_keys = ["app_name", "controller_instance_count", "controller_instance_info"]
                keys = data.keys()
                if len(keys) != len(expected_keys):
                    return generate_response(
                        data="Expected %d keys but got %d" % (len(expected_keys), len(keys)),
                        message="Expected %d keys but got %d" % (len(expected_keys), len(keys)),
                        status=HTTP_400_BAD_REQUEST
                    )
                for k in expected_keys:
                    if k not in keys:
                        return generate_response(
                            data="Missing key: %s" % (k),
                            message="Missing key: %s" % (k),
                            status=HTTP_400_BAD_REQUEST
                        )
    # upload_file(inpFile, fileName, filePath)
    return generate_response(
        message="Validation successful", status=HTTP_200_OK
    )