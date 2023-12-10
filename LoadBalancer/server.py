from flask import Flask
from flask_cors import cross_origin
from flask import request

app = Flask(__name__)


@app.route("/", methods=['GET'])
@cross_origin()
def serve():
    print("request received")
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    port = request.environ.get('SERVER_PORT')
    return f"Server running at {ip}:{port}"


@app.route('/heartbeat', methods=['GET'])
@cross_origin()
def heartbeat():
    return "OK", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7200, debug=True, threaded=True)


# docker run --name name1 -d -p 30000:7200 image_name