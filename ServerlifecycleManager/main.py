from flask import Flask
from flask_cors import cross_origin
from logger import logger

app = Flask(__name__)


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    return "Hi, this is Server Lifecycle manager"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    logger.info("Health Checked")
    return "Ok"


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("/logs/serverlcmgr_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-10:]):
            logs += line

    print(logs)
    return {"logs": logs}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
