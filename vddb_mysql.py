import MySQLdb as mysql
from datetime import datetime
from secrets import choice
import string

alphabet = string.ascii_letters + string.digits

hostname = 'localhost'
username = 'nikodim'
password = 'cy@VdQyj8NyW6Zb'
database = 'nikodim$vddb'

user_id = None
diary_id = None
rec_id = None

# Simple routine to run a query on a database and print the results:
db = mysql.connect(host=hostname, user=username, passwd=password, db=database, charset="utf8",
                   use_unicode=True)  # connect to MySQL DB
cursor = db.cursor()


def findUserByLogin(login):
    sql = 'SELECT UserID FROM users WHERE Login = %s'
    cursor.execute(sql, (login,))
    userid = cursor.fetchone()[0]
    return userid


def createUser(name, login, password):
    sql = 'INSERT INTO users (Name, Login, Password) VALUES (%s, %s, %s)'
    cursor.execute(sql, (name, login, password))
    db.commit()
    return findUserByLogin(login)


def createDiary(user_id, name):
    sql = 'INSERT INTO diaries (UserID, Name) VALUES (%s, %s)'
    cursor.execute(sql, (user_id, name))
    db.commit()
    sql = 'SELECT DiaryID FROM diaries WHERE UserID = %s and Name = %s'
    cursor.execute(sql, (user_id, name))
    diaryid = cursor.fetchone()[0]
    return diaryid


def createRecord(diary_id, title, text):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #    sql = 'INSERT INTO records (DiaryID, CreationDateTime, Title, Text) VALUES ({}, "{}", "{}", "{}")'.format(diary_id,
    #                                                                                                      dt,
    #                                                                                                      title, text)
    sql = 'INSERT INTO records (DiaryID, CreationDateTime, Title, Text) VALUES (%s, %s, %s, %s)'
    cursor.execute(sql, (diary_id, dt, title, text))
    db.commit()
    sql = 'SELECT RecID FROM records WHERE DiaryID = %s and CreationDateTime = %s'
    cursor.execute(sql, (diary_id, dt))
    recid = cursor.fetchone()[0]
    return recid

def utCreateRecords():
    user_id = createUser('nikodim', 'chetverikovnik@yandex.ru', ''.join(choice(alphabet) for i in range(14)))
    # user_id = findUserByLogin('chetverikovnik@yandex.ru')
    diary_id = createDiary(user_id, 'записки лешего'.encode())
    rec_id = createRecord(diary_id, '14 ноября 2021 года. утро'.encode(),
                      'Не следует, однако забывать, что постоянный количественный рост и сфера нашей активности требуют от нас анализа дальнейших'
                      ' направлений развития. Повседневная практика показывает, что постоянное информационно-пропагандистское обеспечение нашей деятельности'
                      ' в значительной степени обуславливает создание системы обучения кадров, соответствует насущным потребностям. Задача организации,'
                      'в особенности же новая модель организационной деятельности обеспечивает широкому кругу (специалистов) участие в формировании позиций,'
                      'занимаемых участниками в отношении поставленных задач. Таким образом рамки и место обучения кадров представляет собой интересный'
                      ' эксперимент проверки модели развития. Повседневная практика показывает, что реализация намеченных плановых заданий представляет'.encode())

db.close()
