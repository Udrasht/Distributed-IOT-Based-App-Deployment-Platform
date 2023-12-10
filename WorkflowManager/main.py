from flask import Flask, request
from flask_cors import cross_origin
from logger import logger
from code_generatoy import generate_code

app = Flask(__name__)


def give_generated_code(workflow_config_json):
    return generate_code(workflow_details=workflow_config_json)


@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    return "Hi, this is Workflow Manager"


@app.route("/health", methods=['GET'])
@cross_origin()
def health():
    logger.info("Health Chewcked")
    return "Ok"


@app.route("/get_logs", methods=['GET'])
@cross_origin()
def get_logs():
    logs = ""
    with open("/logs/workflowmgr_logs.log", "r") as log_file:
        for line in (log_file.readlines()[-10:]):
            logs += line

    print(logs)
    return {"logs": logs}


@app.route("/workflow/codegenerator", methods=['POST'])
@cross_origin
def workflow_code_generation():
    workflow_config_json = request.json['workflow_config']
    code = give_generated_code(workflow_config_json['workflow'])
    return code, 200, {'Content-Type': 'text/plain'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)
