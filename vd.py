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


@route("/", method='POST')
def main():
    print('main route')
    print(request)
    req = request.json
    print(req)
    logger.debug(req)

    response = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }

    user_name = None
    user_id = req['session']['user']['user_id']
    print('Getting user ' + user_id)
    user = vddb.getUser(user_id)
    print(user)
    wait_for_name = False

    if user:
        response['response']['text'] = 'Приветствую, {}'.format(user[1])
    else:
        if wait_for_name:
            vddb.createUser(user_id, req['request']['original_utterance'])
        else:
            response['response']['text'] = 'Здравствуйте, новый пользователь. Как Вас зовут?'
            wait_for_name = True

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


application = default_app()

#run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if os.environ.get('APP_LOCATION') == 'heroku':
    print('Running on heroku')
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=4044, debug=True)
    print('Running locally')

vddb.closeConnection()
