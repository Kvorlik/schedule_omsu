import pymysql
import datetime
from datetime import timedelta

days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", 'Суббота', 'Воскресенье']


class VkBotStudent:

    def __init__(self, user_id):
        print("\nСоздан объект бота!")

        self._USER_ID = user_id

        self._COMMANDS = ["Начать", "Расписание", "На сегодня",
                          "На завтра", "На неделю", "Изменить группу"]

    def registrationUser(self, message):
        nmGroup = message[11:].upper()
        if message[0:10] == self._COMMANDS[1]:
            con = pymysql.Connect('localhost', 'root', '', 'schedule')
            cur = con.cursor()
            cur.execute(f'SELECT DISTINCT schedule.group FROM schedule WHERE schedule.group = "{nmGroup}"')
            rows = cur.fetchall()
            if not rows:
                cur.close()
                con.close()
                return False
            else:
                cur.execute(f'SELECT users.userId FROM users '
                            f'WHERE users.nameGroup !="" AND users.userId = {self._USER_ID}')
                rows1 = cur.fetchall()
                cur.execute(f'SELECT users.userId FROM users '
                            f'WHERE users.nameGroup ="" AND users.userId = {self._USER_ID}')
                rows2 = cur.fetchall()
                if rows2:
                    cur.execute(f'UPDATE users SET `nameGroup` = "{nmGroup}" '
                                f'WHERE users.userId = {self._USER_ID}')
                    con.commit()
                elif rows1:
                    cur.execute(f'UPDATE users SET `nameGroup` = "{nmGroup}" '
                                f'WHERE users.userId = {self._USER_ID}')
                    con.commit()
                else:
                    with con.cursor() as cursor:
                        sql = "INSERT INTO `users` (`userId`, `nameGroup`) VALUES (%s, %s)"
                        cursor.execute(sql, (self._USER_ID, nmGroup))
                    con.commit()
                cur.close()
                con.close()
                return True

    def checkUser(self):
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        cur = con.cursor()
        cur.execute(f'SELECT users.userId FROM users WHERE users.userId = {self._USER_ID} AND users.nameGroup != ""')
        rows = cur.fetchall()
        if not rows:
            print('Вы не зарегистрированы. Чтобы пройти регистрацию напишите "Расписание ИМЯ-ВАШЕЙ-ГРУППЫ"')
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

    def selectGroupUser(self):
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        cur = con.cursor()
        cur.execute(f'SELECT users.nameGroup FROM users WHERE users.userId = {self._USER_ID}')
        rows = cur.fetchall()
        cur.close()
        con.close()
        return rows[0][0]

    def changeGroupUser(self, group):
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        cur = con.cursor()
        cur.execute(f'SELECT schedule.group FROM schedule WHERE schedule.group = "{group}"')
        rows = cur.fetchall()
        if rows:
            cur.execute(f'UPDATE users SET users.nameGroup = "{group}" WHERE users.userId = {self._USER_ID}')
            con.commit()
            cur.close()
            con.close()
            return 'Вы успешно изменили группу.'
        else:
            cur.close()
            con.close()
            return 'Такой группы в базе нет. Попробуйте еще раз.'

    def new_message(self, message):
        if message == self._COMMANDS[0]:
            if self.checkUser():
                return 'Вы уже зарегистрированы в системе.'
            else:
                return 'Для начала необходимо пройти регистрацию. Чтобы пройти регистрацию напишите "Расписание ' \
                   'ИМЯ-ВАШЕЙ-ГРУППЫ". Имя группы необходимо писать полностью и большими буквами. Например: ' \
                       'Расписание ИБД-601-О '
        if self.checkUser():
            # На сегодня
            if message == self._COMMANDS[2]:
                return self._get_sсhedule_today(self.selectGroupUser())

            # На завтра
            elif message == self._COMMANDS[3]:
                return self._get_sсhedule_nextday(self.selectGroupUser())

            # На неделю
            elif message == self._COMMANDS[4]:
                return self._get_sсhedule_week(self.selectGroupUser())

            elif message[:15] == self._COMMANDS[5]:
                return self.changeGroupUser(message[16:])

            elif message[:22] == 'Изменить преподавателя':
                print("qweqweqe")
                return 'Выберите режим "Преподаватель".'

            elif message == 'Студент' or 'Преподаватель':
                return None
            else:
                return 'Я вас не понимаю'
        else:
            if self.registrationUser(message):
                return 'Вы успешно зарегистрировались в системе'
            elif message[0:10] == self._COMMANDS[1]:
                return 'Такой группы в базе нет. Попробуйте еще раз.'
            else:
                return 'Вы не зарегистрированы. Чтобы пройти регистрацию напишите "Расписание ИМЯ-ВАШЕЙ-ГРУППЫ"'


    @staticmethod
    def _get_sсhedule_today(group_name) -> list:
        data = datetime.date.today().strftime("%d.%m.%Y")
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        cur = con.cursor()
        cur.execute(f'SELECT S.discipline, S.group, tc.shortname, r.shortname, tm.dateTime, '
                    f'tm.dateFrom, tm.dateTo FROM SCHEDULE AS S INNER JOIN timewindow AS tm '
                    f'INNER JOIN rooms AS r INNER JOIN teachers AS tc WHERE '
                    f'S.indexTime = tm.indexTime AND S.roomId = r.roomId AND '
                    f'S.teacherIndex = tc.teacherId AND '
                    f'S.group = "{group_name}" AND tm.dateTime = "{data}"')
        rows = cur.fetchall()
        result = '&#128206; ' + days[datetime.date.today().weekday()] + '\n' + '------------------' \
                                                                               '----------------------------' + '\n'
        if not rows:
            cur.close()
            con.close()
            return 'Пар нет'
        for day in rows:
            result = result + (f'&#128467; {day[4]}\n&#128338; {day[5]} - {day[6]}\n'
                               f'&#128204; {day[0]}\n&#128100; {day[2]}\n&#128682; в {day[3]}') + '\n'
            result = result + '----------------------------------------------' + '\n'
        cur.close()
        con.close()
        return result

    @staticmethod
    def _get_sсhedule_nextday(group_name) -> list:
        con = pymysql.Connect('localhost', 'root', '', 'schedule')
        data = datetime.date.today() + timedelta(1)
        data = data.strftime("%d.%m.%Y")
        cur = con.cursor()
        cur.execute(f'SELECT S.discipline, S.group, tc.shortname, r.shortname, tm.dateTime, '
                    f'tm.dateFrom, tm.dateTo FROM SCHEDULE AS S INNER JOIN timewindow AS tm '
                    f'INNER JOIN rooms AS r INNER JOIN teachers AS tc WHERE '
                    f'S.indexTime = tm.indexTime AND S.roomId = r.roomId AND '
                    f'S.teacherIndex = tc.teacherId AND '
                    f'S.group = "{group_name}" AND tm.dateTime = "{data}"')
        rows = cur.fetchall()
        print(rows)
        nextday = datetime.date.today() + timedelta(1)
        result = days[nextday.weekday()] + '\n' + '---------------------------' + '\n'
        if not rows:
            cur.close()
            con.close()
            return 'Пар нет'
        for day in rows:
            result = result + (
                f'&#128467;{day[4]}\n&#128338;{day[5]} - {day[6]}\n&#128204;{day[0]}\n&#128100;'
                f'{day[2]}\n&#128682; в {day[3]}') + '\n'
            result = result + '---------------------------'
        cur.close()
        con.close()
        return result

    @staticmethod
    def _get_sсhedule_week(group_name) -> list:
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
                        f'S.group = "{group_name}" AND tm.dateTime = "{data}"')
            rows = cur.fetchall()
            if not rows:
                result = result + day + ': Пар нет' + '\n'
            else:
                result = result + '\n' + day + '\n'
            for row in rows:
                result = result + '---------------------------' + '\n'
                result = result + (
                    f'&#128467;{row[4]}\n&#128338;{row[5]} - {row[6]}\n&#128204;{row[0]}\n'
                    f'&#128100;{row[2]}\n&#128682; в {row[3]}') + '\n'
                result = result + '---------------------------' + '\n'
        cur.close()
        con.close()
        return result
