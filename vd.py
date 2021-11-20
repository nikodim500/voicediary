from bottle import default_app, route, view, request, static_file, template, run
import logging
from logging.handlers import RotatingFileHandler
import os
import datetime as dt
import json
import vddb_postgresql as vddb

# Enable logging on local filesystem

this_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(this_path, 'logs')
log_file = os.path.join(log_path, __name__ + '.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler(log_file, maxBytes=4194304, backupCount=3)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

vddb.initConnection()

logger.debug('----------------==============>>>>>>>>>>>>>> STARTED <<<<<<<<<<<<<<<=============---------------------')
print('----------------==============>>>>>>>>>>>>>> STARTED <<<<<<<<<<<<<<<=============---------------------')

req_count = 0
session_id = ""
new_session = False

@route("/", method='POST')
def main():
    global req_count, session_id, new_session
    print('main route')
    print(request)
    req = request.json
    print(req)
    logger.debug(req)

    req_count += 1
    print('Request count = {}'.format(req_count))

    response = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }
    # TODO: save json to DB

    if session_id != req['session']['session_id']:
        new_session = True
        session_id = req['session']['session_id']

    user_name = None
    user_id = req['session']['user']['user_id']
    print('Getting user ' + user_id)
    user = vddb.getUser(user_id)

    if user:
        print(user)
        user_name = user[1]
        if user_name:
            if new_session:
                response['response']['text'] = 'Приветствую, {}'.format(user[1])
        else:
            user_name = req['request']['original_utterance']
            user = vddb.updateUserName(user_id, user_name)
            response['response']['text'] = 'Пользователь {} создан'.format(user[1])

        print(user)
        diary = vddb.getDiary(user[5])
        if diary:
            diary_id = diary[0]
            diary_name = diary[3]
            if diary_name:
                response['response']['text'] = 'Дальше ничего не придумали. Импровизируй!'
            else:
                if new_session:
                    response['response']['text'] = 'У вас нет дневников. Давайте создадим новый. Скажите название дневника'
                else:
                    diary_name = req['request']['original_utterance']
                    diary = vddb.updateDiary(diary_id, diary_name)
                    response['response']['text'] = 'Дневник {} создан'.format(diary[3])
        else:
            diary = vddb.createDiary(user_id)
            response['response']['text'] = response['response']['text'] + '. ' + 'У вас нет дневников. Давайте создадим новый. Скажите название дневника'
    else:
        print('New user!')
        user = vddb.createUser(user_id)
        response['response']['text'] = 'Здравствуйте, новый пользователь. Как Вас зовут?'

    return json.dumps(response)


@route('/static/<filename:path>')  # Ensure css files in ./static are accessible
def send_static(filename):
    return static_file(filename, root='./static/')


@route('/about')
@view('home')
def home():
    """Renders the home page."""
    return dict(
        year=dt.date.today().year,
        appname='Voice Diary',
        owner='© Nikolay Chetverikov'
    )


@route('/log')
def log():
    return static_file(log_file, log_path)

@route('/ping')
def ping():
    return "pong"

application = default_app()

#run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if os.environ.get('APP_LOCATION') == 'heroku':
    print('Running on heroku')
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=4044, debug=True)
    print('Running locally')

vddb.closeConnection()
