from flask import Flask, request
import requests
from queue import Queue
import random
import os

queue = Queue()

responseData = {}
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'OK'

@app.route('/telegram/webhook', methods=['POST'])
def webhook_telegram():
    print(request.json)
    return 'OK'

@app.route('/telegram/check-use-in-channel/', methods=['POST'])
def telegram_check_user_in_channel():
    key_api = os.environ.get('TELEGRAM_BOT_API')
    body = request.json
    chat_id = body.get('chat_id')
    user_id = body.get('user_id')
    url = f"https://api.telegram.org/bot{key_api}/getChatMember?chat_id={chat_id}&user_id={user_id}"
    response = requests.request("POST", url, headers={}, data={})
    return response.json()

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

@app.route('/discord/check_user_in_server', methods=['POST'])
def check_user_in_server():
    keyBot = os.environ.get('DISCORD_BOT_API')
    headers = {
    'Authorization': f'Bot {keyBot}'
    }
    params = {
        'limit': 1000
    }
    body = request.json
    guild_id = body.get('guild_id')
    user_id = body.get('user_id')

    response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/members', headers=headers, params=params)
    members = response.json()
    for member in members:
        if str(user_id) == str(member.get('user').get("id")):
            return member.get('user')
    return {"status":"False"}

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)