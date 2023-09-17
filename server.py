from flask import Flask, request
from queue import Queue
import random
from cachetools import TTLCache

responseData = TTLCache(maxsize=1000000, ttl=600)

queue = Queue()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'OK'

@app.route('/twitter/create-task/', methods=['POST'])
def twitter_create_task():
    idTask = random.randint(11111111111111111,999999999999999999)
    data = request.json
    data = {**dict(data),"idTask":idTask}
    queue.put(data)
    return data

@app.route('/twitter/get-task/', methods=['GET'])
def twitter_bot_get_task():
    if(queue.empty() == True):
        return "EMPTY" 
    return queue.get()


@app.route('/twitter/set-task-value/<id>', methods=['POST'])
def twitter_bot_set_task_value(id):
    body = request.json
    responseData[id] = body
    return body

@app.route('/twitter/get-task-value/<id>', methods=['GET'])
def twitter_bot_get_task_value(id):
    if responseData.get(id) == None:
        return {}
    return responseData.get(id)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
