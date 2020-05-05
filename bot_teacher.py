import pymysql
import datetime
from datetime import timedelta

days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", 'Суббота', 'Воскресенье']


class VkBotTeacher:

    def __init__(self, user_id):
        print("\nСоздан объект бота!")

        self._USER_ID = user_id

        self._COMMANDS = ["Начать", "Расписание", "На сегодня",
                          "На завтра", "На неделю", "Искать по группе",
                          "Искать по преподавателю"]

    def registrationUser(self, message):
        nmTeacher = message[11:]
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        if message[0:10] == self._COMMANDS[1]:
            cur = con.cursor()
            cur.execute(f'SELECT DISTINCT teachers.shortname FROM teachers WHERE teachers.shortname = "{nmTeacher}"')
            rows = cur.fetchall()
            if not rows:
                con.close()
                return False
            else:
                cur.execute(f'SELECT users.userId FROM users '
                            f'WHERE users.nameTeacher !="" AND users.userId = {self._USER_ID}')
                rows1 = cur.fetchall()
                cur.execute(f'SELECT users.userId FROM users '
                            f'WHERE users.nameTeacher ="" AND users.userId = {self._USER_ID}')
                rows2 = cur.fetchall()
                if rows2:
                    cur.execute(f'UPDATE users SET `nameTeacher` = "{nmTeacher}" '
                                f'WHERE users.userId = {self._USER_ID}')
                    con.commit()
                elif rows1:
                    cur.execute(f'UPDATE users SET `nameTeacher` = "{nmTeacher}" '
                                f'WHERE users.userId = {self._USER_ID}')
                    con.commit()
                else:
                    with con.cursor() as cursor:
                        sql = "INSERT INTO `users` (`userId`, `nameTeacher`) VALUES (%s, %s)"
                        cursor.execute(sql, (self._USER_ID, nmTeacher))
                    con.commit()
                cur.close()
                con.close()
                return True

    def checkUser(self):
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        cur = con.cursor()
        cur.execute(f'SELECT users.userId FROM users WHERE users.userId = {self._USER_ID} AND users.nameTeacher != ""')
        rows = cur.fetchall()
        if not rows:
            print('Вы не зарегистрированы. Чтобы пройти регистрацию напишите "Расписание ИМЯ-ПРЕПОДАВАТЕЛЯ"')
            cur.close()
            con.close()
            return False
        else:
            user = str(rows[0])[1:-2]
            if user == str(self._USER_ID):
                print('Пользователь есть в базе')
                cur.close()
                con.close()
                return True

    def selectTeacherUser(self):
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        cur = con.cursor()
        cur.execute(f'SELECT users.nameTeacher FROM users WHERE users.userId = {self._USER_ID}')
        rows = cur.fetchall()
        cur.close()
        con.close()
        return rows[0][0]

    def new_message(self, message):
        if message == self._COMMANDS[0]:
            if self.checkUser():
                return 'Вы уже зарегистрированы в системе.'
            else:
                return 'Для начала необходимо пройти регистрацию. Чтобы пройти' \
                       ' регистрацию напишите "Расписание Фамилия И.О.". Например: Иванов И.И.'
        elif self.checkUser():
            # На сегодня
            if message == self._COMMANDS[2]:
                return self._get_sсhedule_today(self.selectTeacherUser())

            # На завтра
            elif message == self._COMMANDS[3]:
                return self._get_sсhedule_nextday(self.selectTeacherUser())

            # На неделю
            elif message == self._COMMANDS[4]:
                return self._get_sсhedule_week(self.selectTeacherUser())

            else:
                return 'Я вас не понимаю'
        else:
            if self.registrationUser(message):
                return 'Вы успешно зарегистрировались в системе'
            elif message[0:10] == self._COMMANDS[1]:
                return 'Такого преподавателя в базе нет. Попробуйте еще раз.'
            else:
                return 'Вы не зарегистрированы. Чтобы пройти регистрацию напишите "Расписание Фамилия И.О."'


    @staticmethod
    def _get_sсhedule_today(teacher_name) -> list:
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        data = datetime.date.today().strftime("%d.%m.%Y")
        cur = con.cursor()
        cur.execute(f'SELECT S.discipline, S.group, tc.shortname, r.shortname, tm.dateTime, '
                f'tm.dateFrom, tm.dateTo FROM SCHEDULE AS S INNER JOIN timewindow AS tm '
                f'INNER JOIN rooms AS r INNER JOIN teachers AS tc WHERE '
                f'S.indexTime = tm.indexTime AND S.roomId = r.roomId AND '
                f'S.teacherIndex = tc.teacherId AND '
                f'tc.shortname = "{teacher_name}" AND tm.dateTime = "{data}"')
        rows = cur.fetchall()
        result = '&#128206; ' + days[datetime.date.today().weekday()] + '\n' + '------------------' \
                                                                               '----------------------------' + '\n'
        if not rows:
            cur.close()
            con.close()
            return 'Пар нет'
        for day in rows:
            result = result + (f'&#128467; {day[4]}\n&#128338; {day[5]} - {day[6]}\n&#128204; {day[0]}\n&#128193;'
                               f'{day[1]}\n&#128100; {day[2]}\n&#128682; в {day[3]}') + '\n'
            result = result + '----------------------------------------------' + '\n'
        cur.close()
        con.close()
        return result

    @staticmethod
    def _get_sсhedule_nextday(teacher_name) -> list:
        data = datetime.date.today() + timedelta(1)
        data = data.strftime("%d.%m.%Y")
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        cur = con.cursor()
        cur.execute(f'SELECT S.discipline, S.group, tc.shortname, r.shortname, tm.dateTime, '
                f'tm.dateFrom, tm.dateTo FROM SCHEDULE AS S INNER JOIN timewindow AS tm '
                f'INNER JOIN rooms AS r INNER JOIN teachers AS tc WHERE '
                f'S.indexTime = tm.indexTime AND S.roomId = r.roomId AND '
                f'S.teacherIndex = tc.teacherId AND '
                f'tc.shortname = "{teacher_name}" AND tm.dateTime = "{data}"')
        rows = cur.fetchall()
        nextday = datetime.date.today() + timedelta(1)
        result = days[nextday.weekday()] + '\n' + '---------------------------' + '\n'
        if not rows:
            cur.close()
            con.close()
            return 'Пар нет'
        for day in rows:
            result = result + (
                f'&#128467;{day[4]}\n&#128338;{day[5]} - {day[6]}\n&#128204;{day[0]}\n&#128193;{day[1]}\n&#128100;{day[2]}\n&#128682; в {day[3]}') + '\n'
            result = result + '---------------------------'
        cur.close()
        con.close()
        return result

    @staticmethod
    def _get_sсhedule_week(teacher_name) -> list:
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        week_day = datetime.date.today().weekday()
        result = ''
        for day in days:
            data = datetime.date.today() - timedelta(week_day - days.index(day))
            data = data.strftime("%d.%m.%Y")
            cur = con.cursor()
            cur.execute(f'SELECT S.discipline, S.group, tc.shortname, r.shortname, tm.dateTime, '
                f'tm.dateFrom, tm.dateTo FROM SCHEDULE AS S INNER JOIN timewindow AS tm '
                f'INNER JOIN rooms AS r INNER JOIN teachers AS tc WHERE '
                f'S.indexTime = tm.indexTime AND S.roomId = r.roomId AND '
                f'S.teacherIndex = tc.teacherId AND '
                f'tc.shortname = "{teacher_name}" AND tm.dateTime = "{data}"')
            rows = cur.fetchall()
            if not rows:
                result = result + day + ': Пар нет' + '\n'
            else:
                result = result + '\n' + day + '\n'
            for row in rows:
                result = result + '---------------------------' + '\n'
                result = result + (
                    f'&#128467;{row[4]}\n&#128338;{row[5]} - {row[6]}\n&#128204;{row[0]}\n&#128193;{row[1]}\n&#128100;{row[2]}\n&#128682; в {row[3]}') + '\n'
                result = result + '---------------------------' + '\n'
        cur.close()
        con.close()
        return result
