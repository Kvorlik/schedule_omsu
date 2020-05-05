import pymysql
from bs4 import BeautifulSoup

con = pymysql.Connect('localhost', 'root',
                      '', 'schedule')


with open('shedule.xml', encoding="utf-8") as raw_resuls:
    results = BeautifulSoup(raw_resuls, 'xml')

def deleteTables():
    cur = con.cursor()
    sql = 'DROP TABLE schedule, rooms, teachers, timewindow, users'
    cur.execute(sql)
    con.commit()

def insertRooms():
    for element in results.find_all("Rooms"):
        for room in element.find_all("Room"):
            cur = con.cursor()
            sql = 'INSERT INTO rooms(`roomId`, `shortname`, `building`) VALUES (%s, %s, %s)'
            cur.execute(sql, (room['Index'], room['ShortName'], room['Building']))
            con.commit()
            print(room['Index'], room['ShortName'], room['Building'])


def insertTeacher():
    for element in results.find_all("Teachers"):
        for teacher in element.find_all("Teacher"):
            cur = con.cursor()
            sql = 'INSERT INTO teachers(`teacherId`, `name`, `shortname`) VALUES (%s, %s, %s)'
            cur.execute(sql, (teacher['Index'], teacher['Name'], teacher['ShortName']))
            con.commit()
            print(teacher['Index'], teacher['Name'], teacher['ShortName'])


def insertTimewindow():
    for element in results.find_all("TimeWindows"):
        for timewindow in element.find_all("TimeWindow"):
            cur = con.cursor()
            sql = 'INSERT INTO timewindow(`indexTime`, `dateTime`, `dateFrom`, `dateTo`) ' \
                  'VALUES (%s, %s, %s, %s)'
            cur.execute(sql, (int(timewindow['Index']), timewindow['Date'], timewindow['From'], timewindow['To']))
            con.commit()
            print(timewindow['Index'], timewindow['Date'], timewindow['From'], timewindow['To'])


def insertSchedule():
    for element in results.find_all("Schedule"):
        for strSchedule in element.find_all("StringOfSchedule"):
            cur = con.cursor()
            sql = 'INSERT INTO schedule(`discipline`, `indexTime`, `teacherIndex`, `roomId`, `group`) ' \
                  'VALUES (%s, %s, %s, %s, %s)'
            cur.execute(sql, (strSchedule['Discipline'], strSchedule['Index'],
                              strSchedule['Teacher'], strSchedule['Room'], strSchedule['Group']))
            con.commit()
            print(strSchedule['Discipline'], strSchedule['Index'],
                  strSchedule['Teacher'], strSchedule['Room'], strSchedule['Group'])


# deleteTables()
# insertRooms()
# insertTeacher()
# insertTimewindow()
# insertSchedule()

