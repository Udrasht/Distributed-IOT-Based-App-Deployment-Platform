# flask app
from flask import Flask,render_template,jsonify, request
import json
import requests

app = Flask(__name__,template_folder='./')


@app.route("/api/options")
def options():
    locations = requests.get('http://localhost:8050/api/sensor/location')
    locations = locations.json()
    options=[]
    for location in locations:
        elem = {}
        elem['label']=location
        elem['value']=location
        options.append(elem)
    print(options)
    # options = [{'label': 'Option 1', 'value': 'option1'},
    #            {'label': 'Option 2', 'value': 'option2'},
    #            {'label': 'Option 3', 'value': 'option3'}]
    return jsonify(options)

@app.route("/")
def index():
    return render_template('./index.html')

@app.route('/api/data')
def get_api_data():
    stop = request.args.get('stop')
    if stop:
        return jsonify({'status': 'stopped'})
    else:
        response = requests.get('http://localhost:8050/api/sensor/data/latest/AQ-KN00-00?last=1')
        if response.status_code == 200:
            print(response.json())
            return jsonify(response.json())
        else:
            return jsonify({'error': 'API call failed'})


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=9010)



