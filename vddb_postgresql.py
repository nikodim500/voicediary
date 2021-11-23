import os
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timezone
from secrets import choice
import string

alphabet = (string.ascii_letters + string.digits).translate({ord(c): None for c in 'IO0'})

# DATABASE_URL = os.environ['DATABASE_URL']

DATABASE_URL = os.environ.get('DATABASE_URL')
print('DATABASE_URL = ' + DATABASE_URL)

connection = None
cursor = None


def initConnection():
    global connection, cursor, DATABASE_URL
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
    except (Exception, Error) as error:
        print("Ошибка инициации PostgreSQL", error)
        return False
    return True


def closeConnection():
    global connection
    connection.close()


def findUserByLogin(login):
    global cursor
    sql = 'SELECT user_id FROM public.user WHERE user_login = %s'
    cursor.execute(sql, (login,))
    userid = cursor.fetchone()[0]
    return userid


def createUser(id, name=None, login=None, password=None):
    global connection, cursor
    sql = 'INSERT INTO public.user (user_id, user_name, user_login, user_pwd) VALUES (%s, %s, %s, %s)'
    cursor.execute(sql, (id, name, login, password))
    connection.commit()
    sql = 'SELECT * FROM public.user WHERE user_id = %s'
    cursor.execute(sql, (id,))
    user = cursor.fetchone()
    return user


def updateUser(id, name, login, password):
    global connection, cursor
    sql = 'UPDATE public.user SET (user_name, user_login, user_pwd) = (%s, %s, %s) WHERE user_id = %s'
    cursor.execute(sql, (name, login, password, id))
    connection.commit()
    sql = 'SELECT * FROM public.user WHERE user_id = %s'
    cursor.execute(sql, (id,))
    user = cursor.fetchone()
    return user

def updateUserField(id, field, value):
    global connection, cursor
    sql = 'UPDATE public.user SET ' + field + ' = %s WHERE user_id = %s'
    cursor.execute(sql, (value, id))
    connection.commit()
    sql = 'SELECT * FROM public.user WHERE user_id = %s'
    cursor.execute(sql, (id,))
    user = cursor.fetchone()
    return user

def updateUserName(id, name):
    return updateUserField(id, "user_name", name)

def updateUserLogin(id, login):
    return updateUserField(id, "user_login", login)

def updateUserPassword(id, pwd):
    return updateUserField(id, "user_pwd", pwd)


def getUser(id):
    global connection, cursor
    sql = 'SELECT * FROM public.user WHERE user_id = %s'
    cursor.execute(sql, (id,))
    user = cursor.fetchone()
    return user

def createDiary(user_id, name=None):
    global connection, cursor
    # Insert new record into diary
    sql = 'INSERT INTO diary (user_id, diary_name) VALUES (%s, %s)'
    cursor.execute(sql, (user_id, name))
    connection.commit()
    # Retreive ID of new record
    sql = 'SELECT * FROM diary WHERE user_id = %s and diary_name = %s'
    cursor.execute(sql, (user_id, name))
    diary = cursor.fetchone()
    return diary

def updateDiary(diary_id, name):
    global connection, cursor
    # Update diary
    sql = 'UPDATE diary SET diary_name = %s WHERE diary_id = %s'
    cursor.execute(sql, (name, diary_id))
    connection.commit()
    # Retreive ID of new record
    sql = 'SELECT * FROM diary WHERE diary_id = %s'
    cursor.execute(sql, (diary_id,))
    diary = cursor.fetchone()
    return diary

def getDiary(diary_id):
    global cursor
    # Retreive current diary
    sql = 'SELECT * FROM diary WHERE diary_id = %s'
    cursor.execute(sql, (diary_id,))
    diary = cursor.fetchone()
    return diary


def createRecord(diary_id, title=None):
    global connection, cursor
    dt = datetime.now(timezone.utc)
    sql = 'INSERT INTO record (diary_id, created_at, record_title) VALUES (%s, %s, %s)'
    cursor.execute(sql, (diary_id, dt, title))
    connection.commit()
    sql = 'SELECT * FROM record WHERE diary_id = %s and created_at = %s'
    cursor.execute(sql, (diary_id, dt))
    record = cursor.fetchone()
    return record

def updateRecordTitle(record_id, title):
    global connection, cursor
    dt = datetime.now(timezone.utc)
    sql = 'UPDATE record SET record_title = %s, changed_at = %s WHERE record_id = %s'
    cursor.execute(sql, (title, dt, record_id))
    connection.commit()
    sql = 'SELECT * FROM record WHERE record_id = %s'
    cursor.execute(sql, (record_id,))
    record = cursor.fetchone()
    return record

def updateRecordText(record_id, text):
    global connection, cursor
    dt = datetime.now(timezone.utc)
    sql = 'UPDATE record SET changed_at = %s, record_text = CASE WHEN record_text IS NULL THEN %s ELSE record_text || ". " || %s END WHERE record_id = %s'
    cursor.execute(sql, (dt, text, text, record_id))
    connection.commit()
    sql = 'SELECT * FROM record WHERE record_id = %s'
    cursor.execute(sql, (record_id,))
    record = cursor.fetchone()
    return record

def getRecord(id):
    global connection, cursor
    sql = 'SELECT * FROM record WHERE record_id = %s'
    cursor.execute(sql, (id,))
    record = cursor.fetchone()
    return record


# Unit tests
def utCreateRecords():
    global alphabet
    user = createUser('j3493nJWIE3894R3KJ8Fkdkd8')
    print(user)
    user = updateUser('j3493nJWIE3894R3KJ8Fkdkd8', 'Брат Онуфрий', 'chetver@yandex.ru',
                      ''.join(choice(alphabet) for i in range(14)))
    print(user)
    user_id = user[0]
    # user_id = findUserByLogin('chetverikovnik@yandex.ru')
    diary = createDiary(user_id, 'записки лешего')
    print(diary)
    diary_id = diary[0]
    record = createRecord(diary_id, '14 ноября 2021 года. утро')
    text = 'Не следует, однако забывать, что постоянный количественный рост и сфера нашей активности требуют от нас ' \
           'анализа дальнейших направлений развития. Повседневная практика показывает, что постоянное ' \
           'информационно-пропагандистское обеспечение нашей деятельности в значительной степени обуславливает ' \
           'создание системы обучения кадров, соответствует насущным потребностям. Задача организации, в особенности ' \
           'же новая модель организационной деятельности обеспечивает широкому кругу (специалистов) участие в ' \
           'формировании позиций, занимаемых участниками в отношении поставленных задач. Таким образом рамки и место ' \
           'обучения кадров представляет собой интересный эксперимент проверки модели развития. Повседневная практика ' \
           'показывает, что реализация намеченных плановых заданий представляет'
    print(record)
    record_id = record[0]
    updateRecordText(record_id, text)
