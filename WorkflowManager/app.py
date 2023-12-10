from flask import Flask, render_template
from flask import request, jsonify
import requests

app = Flask(__name__,template_folder='template')

result=[]
def collect_data(location,vertical):
    #collect data
    request_string="https://api/sensor/data/latest/"+location+"/"+vertical
    response = requests.get(request_string)
    data = response.json()
    return jsonify(data)

def check_min_limit(data,limit):
    #check min limit
    if data < limit:
        result[1]=1

def check_max_limit(data,limit):
    #check max limit
    result[2]=1

def print_result(result):
    print(result)
    #print result

# def send_notification():
#     #send notification
    

codeBlocks={
    "block1" : "print('data_collected')\n", # data=collectdata()
    "block2" : "print('minimum-limit-applied')\n",
    "block3" : "print('maximum-limit-applied')\n",
    "block4" : "print('print-result')\n",

    "block5" : "print('send-notification')\n",
    "block6" : "print('function-applied)\n"

}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flow',methods=['POST'])
def get_flow():
    data = request.get_json()
    codeString='import workflow.py\n\n'
    for horizontals in data:
        for blocks in data[horizontals]:
            block_name=blocks[0]
            args=blocks[1:]

            codeString=codeString+codeBlocks[blocks]
    print(codeString)

    with open("generated_code.py","w") as file:
        file.write("import workflow.py")
    


       
            # file.write(codeBlocks[blocks])
        # print(blocks)
   

    # with open("workflow.py", "w") as file:
        
    result = {'message': 'file-created-successfully', 'status': "200"}
    result_json = jsonify(result)
    print(result_json.get_data(as_text=True)) # log the response data
    return result_json


if __name__ == '__main__':
    app.run(debug=True)
