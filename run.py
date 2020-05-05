import vk_api
import random
import json
import pymysql
from bot_student import VkBotStudent
from bot_teacher import VkBotTeacher
from vk_api.longpoll import VkLongPoll, VkEventType

con = pymysql.Connect('localhost', 'root',
                      '', 'schedule')

keyboard = {
    "one_time": False,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "На сегодня"
            },
            "color": "primary"
        }],
        [{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"2\"}",
                "label": "На завтра"
            },
            "color": "primary"
        },
            {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "На неделю"
                },
                "color": "primary"
            }],
        [{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"2\"}",
                "label": "Студент"
            },
            "color": "positive"
        },
            {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Преподаватель"
                },
                "color": "positive"
            },{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"2\"}",
                    "label": "Помощь"
                },
                "color": "primary"
            }]
    ]
}
role = ['студент', 'преподаватель']
users_role = {}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,
                                'keyboard': keyboard, 'random_id': random.randint(1, 2147483647)})


token = "53e33420a6748bc8089bfdacc11f46991442b599d6af32a8ec7c1d045b151c063393c2e5b48ab775e9bbf"

vk = vk_api.VkApi(token=token)

longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            print(event.raw)
            print('New message:')
            print(f'For me by: {event.user_id}', end='')
            # messages = vk.method("messages.getConversations", {"offset": 0, "count": 200, "filter": "unanswered"})
            # print(event.text[0:10])
            print('Text: ', event.text)
            request = event.text
            botStudent = VkBotStudent(event.user_id)
            botTeacher = VkBotTeacher(event.user_id)

            if request.lower() in role:
                choise = request.lower()
                write_msg(event.user_id, ('Вы выбрали категорию ' + choise))
                users_role[event.user_id] = choise
            elif request.lower().startswith('на'):
                try:
                    if users_role[event.user_id] == 'студент':
                        write_msg(event.user_id, botStudent.new_message(request))
                    elif users_role[event.user_id] == 'преподаватель':
                        write_msg(event.user_id, botTeacher.new_message(request))
                except KeyError:
                    write_msg(event.user_id, 'Вы не выбрали категорию(Студент/Преподаватель).')
            elif request[:10].lower() == 'расписание':
                if users_role[event.user_id] == 'студент':
                    write_msg(event.user_id, botStudent.new_message(request))
                elif users_role[event.user_id] == 'преподаватель':
                    write_msg(event.user_id, botTeacher.new_message(request))
            elif request[:15].lower() == 'изменить группу':
                try:
                    if users_role[event.user_id] == 'студент':
                        write_msg(event.user_id, botStudent.new_message(request))
                    elif users_role[event.user_id] == 'преподаватель':
                        write_msg(event.user_id, botTeacher.new_message(request))
                except KeyError:
                    write_msg(event.user_id, 'Вы не выбрали категорию(Студент/Преподаватель).')
            elif request[:22].lower() == 'изменить преподавателя':
                try:
                    if users_role[event.user_id] == 'студент':
                        write_msg(event.user_id, botStudent.new_message(request))
                    elif users_role[event.user_id] == 'преподаватель':
                        write_msg(event.user_id, botTeacher.new_message(request))
                except KeyError:
                    write_msg(event.user_id, 'Вы не выбрали категорию(Студент/Преподаватель).')
            elif request == 'Помощь':
                write_msg(event.user_id, 'Если вы хотите изменить имя группы или преподователя, '
                                         'напишите следующее: \nИзменить группу ИМЯ-ГРУППЫ или'
                                         '\nИзменить преподавателя Фамилия И.О.')
            else:
                write_msg(event.user_id, 'Я вас не понимаю.')
