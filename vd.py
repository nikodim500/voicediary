from bottle import default_app, route, view, request, static_file, template, run
import logging
from logging.handlers import RotatingFileHandler
import os
import datetime as dt
import json
import vddb_postgresql as vddb
from datetime import datetime, timezone

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
wait_for_text = False
wait_for_command = False

@route("/", method='POST')
def main():
    global req_count, session_id, new_session, wait_for_text, wait_for_command
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
    else:
        new_session = False

    user_name = None
    user_id = req['session']['user']['user_id']
    print('Getting user ' + user_id)
    user = vddb.getUser(user_id)

    print('if user {}'.format(user))
    if user:
        user_name = user[1]
        print('if user_name {}'.format(user_name))
        if user_name:
            print('if user_name new session {}'.format(new_session))
            if new_session:
                response['response']['text'] = '??????????????????????, {}'.format(user[1])
        else:
            user_name = req['request']['original_utterance'].title()
            user = vddb.updateUserName(user_id, user_name)
            response['response']['text'] = '???????????????????????? {} ????????????'.format(user[1])

        st = datetime.now(timezone.utc)
        print('start get record: {}'.format(st))
        diary = vddb.getDiary(user[5])
        et = datetime.now(timezone.utc)
        print('end get record: {}, duration: {}'.format(et, et-st))
        print('if diary {}'.format(diary))
        if diary:
            diary_id = diary[0]
            diary_name = diary[3]
            print('if diary_name {}'.format(diary_name))
            if diary_name:
                record = vddb.getRecord(diary[5])
                if record:
                    record_title = record[3]
                    record_text = record[4]
                    if record_title:
                        if record_text:
                            if new_session:
                                response['response']['text'] = '?????? ???????????????? ??????????????: ?????????????????? ????????????, ?????????? ????????????, ?????????????????? ????????????. ???????????????????? ??????????????'
                                wait_for_command = True
                            else:
                                if wait_for_command:
                                    command = req['request']['original_utterance'].lower()
                                    wait_for_command = False
                                    if command == '?????????????????? ????????????':
                                        response['response']['text'] = '?????????????? ???????????????? ????????????. ????????????????'
                                        wait_for_text = True
                                    elif command == '?????????? ????????????':
                                        vddb.createRecord(diary[0])
                                        response['response']['text'] = '?????????????? ???????????????? ?????????? ????????????. ?????????????? ??????????????????'
                                    elif command == '?????????????????? ????????????':
                                        st = datetime.now(timezone.utc)
                                        print('start build text: {}'.format(st))
                                        response['response']['text'] = '???????????? {}. ?????????? ????????????: {}. ?????????? ????????????. ?????? ???????????????? ??????????????: ?????????????????? ????????????, ?????????? ????????????, ?????????????????? ????????????. ???????????????????? ??????????????'.format(record_title, record_text)
                                        wait_for_command = True
                                        et = datetime.now(timezone.utc)
                                        print('end build: {}, duration: {}'.format(et, et - st))
                                    else:
                                        response['response']['text'] = '?????????????? ???? ????????????????????. ?????? ???????????????? ??????????????: ?????????????????? ????????????, ?????????? ????????????, ?????????????????? ????????????. ???????????????????? ??????????????'
                                        wait_for_command = True
                                elif wait_for_text:
                                    record_text = req['request']['original_utterance']
                                    vddb.updateRecordText(record[0], record_text)
                                    response['response']['text'] = '?????????? ??????????????. ???????????????? ????????????'
                                else:
                                    response['response']['text'] = '?????????????? ???????????????? ????????????. ????????????????'
                                    wait_for_text = True
                        else:
                            if new_session:
                                response['response']['text'] = '???? ???? ?????????????????? ???????????? ?? ???????????????????? {}. ???????????????? ?????????? ????????????'.format(record_title)
                                wait_for_text = True
                            else:
                                if wait_for_text:
                                    record_text = req['request']['original_utterance']
                                    print(record_text)
                                    vddb.updateRecordText(record[0], record_text)
                                    response['response']['text'] = '?????????? ??????????????. ???????????????? ????????????'
                                else:
                                    response['response']['text'] = '???????????? ???????????????? ??????????'
                                    wait_for_text = True
                    else: # no record title
                        if new_session:
                            response['response']['text'] = '?? ???????????? ?????? ??????????????????. ?????????????? ??????????????????'
                        else:
                             record_title = req['request']['original_utterance']
                             vddb.updateRecordTitle(record[0], record_title)
                             response['response']['text'] = '?????????????????? ??????????????. ???????????? ???????????????? ??????????'
                else: # no record
                    vddb.createRecord(diary[0])
                    response['response']['text'] = '?? ?????? ?????? ??????????????. ?????????????? ???????????????? ??????????. ?????????????? ??????????????????'
            else:
                if new_session:
                    response['response']['text'] = '?? ?????? ?????? ??????????????????. ?????????????? ???????????????? ??????????. ?????????????? ???????????????? ????????????????'
                else:
                    diary_name = req['request']['original_utterance']
                    diary = vddb.updateDiary(diary_id, diary_name)
                    response['response']['text'] = '?????????????? {} ????????????. ???????????????????'.format(diary[3])

        else:
            diary = vddb.createDiary(user_id)
            response['response']['text'] = response['response']['text'] + '. ' + '?? ?????? ?????? ??????????????????. ?????????????? ???????????????? ??????????. ?????????????? ???????????????? ????????????????'
    else:
        print('New user!')
        user = vddb.createUser(user_id)
        response['response']['text'] = '????????????????????????, ?????????? ????????????????????????. ?????? ?????? ???????????'

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
        owner='?? Nikolay Chetverikov'
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
