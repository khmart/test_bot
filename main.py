import telebot
from flask import Flask, request
import json
import datetime



token = 'your_token_bot'
bot = telebot.TeleBot(token)


#
# secret = 'secret_code'
# url = 'https://your_name.pythonanywhere.com/' + secret
#
# bot = telebot.TeleBot(token, threaded=False)
# bot.remove_webhook()
# bot.set_webhook(url=url)
#
# app = Flask(__name__)
#
# @app.route('/'+secret, methods=['POST'])
# def webhook():
#     update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
#     bot.process_new_updates([update])
#     #return 'Hello from Flask!'
#     return 'ok', 200

user_type = ''

spisok_reg = {}
book = {}
dict_sotr = {}
dict_poputi = {}
botMark = {}

passenger_bron = {}
driver_num_passenger = {}
driver_number = {}

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row('Регистрация')

keyboard_main = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_main.row('Поездка успешно завершена')
keyboard_main.row('Отменить поездку')
# keyboard_main.row('Найти попутчика')

keyboard_start = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_start.row('Хочу поехать')

keyboard_find = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_find.row('Найти попутчика')

keyboard_step = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_step.row('Водитель')
keyboard_step.row('Пассажир')


key_stop = telebot.types.KeyboardButton('остановить поиск')
keyboard_stop = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_stop.row(key_stop)

key_time = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
key_time.row('7:30', '7:45', '8:00', '8:15', '8:30')
key_time.row('16:30', '16:45', '17:00', '17:15', '17:30')
key_time.row('остановить поиск', 'другое время')

key_dopost = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
key_dopost.row('Пропустить')
key_dopost.row('остановить поиск')

key_point = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
key_point.row('Добавить еще промежуточную остановку')
key_point.row('Завершить ввод маршрута')
key_point.row('остановить поиск')

key_num = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
key_num.row('1', '2', '3', '4', '5', '6')

key_market = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
key_market.row('1', '2', '3', '4', '5')


@bot.callback_query_handler(func=lambda call: call.message.text == 'Удалить маршрут')
def answer(call):
    if call.message.text == 'Удалить маршрут':
        if call.from_user.id in dict_sotr:
            name = spisok_reg[call.from_user.id]['name']
            typeUser = dict_sotr[call.from_user.id]['type']
            if typeUser == 'driver':
                if call.from_user.id in book:
                    for i in book[call.from_user.id]:
                        if book[call.from_user.id][i] == True:
                            passenger_bron[i] = False
                            bot.send_message(i, 'Пользователь '+ name +' отменил(а) заявку, вам необходимо посмотреть другие заявки для вашего маршрута')
                        else:
                            pass
                    del book[call.from_user.id]
                # book[int(call.from_user.id)] = [{int(call.data): True}]
            elif typeUser == 'passenger':
                delete = {}
                for key in book:
                    for i in book[key]:
                        if i == int(call.from_user.id):
                            if book[key][i] == True:
                                bot.send_message(key,
                                                 'Пользователь ' + name + ' отменил(а) заявку, вам необходимо посмотреть другие заявки для вашего маршрута')
                                if key in driver_number:
                                    num_driver = driver_number[key]
                                    driver_number[key] = num_driver - 1
                            delete[key] = i
                if delete != {}:
                    for i, j in delete.items():
                        del book[i][j]
                passenger_bron[call.from_user.id] = False
            del dict_sotr[call.from_user.id]
            bot.send_message(call.message.chat.id, 'Маршрут удален', reply_markup=keyboard_start)
            with open('booked.txt', 'a') as f:
                json.dump(book, f)
          
    elif call.message.text == 'Забронировать':
        name = spisok_reg[call.data]['name']
        bot.send_message(call.message.chat.id, 'Вы забронировали машину' + name)


@bot.callback_query_handler(func=lambda call: call.data == 'отказать')
def otkaz(call):
    if call.message.text == 'Отказать':
        if call.from_user.id in book:
            print('отказ в бронировании водитель')
        for i in book:
            if call.from_user.id in book[i]:
                print('отказ в бронировании пассажир')

@bot.callback_query_handler(func=lambda call: call.message.text[:29] == 'Вам предлагает поехать вместе' )
def potverdit(call):
    if call.from_user.id in dict_sotr:
        if call.from_user.id in dict_sotr:
            # for m in dict_sotr[call.from_user.id]:
            if 'infocar' in dict_sotr[call.from_user.id]:
                inf_car = ', машина ' + dict_sotr[call.from_user.id]['infocar']
            else:
                inf_car = ''
            if dict_sotr[call.from_user.id]['dopPoint'] == []:
                message = 'По маршруту: ' + dict_sotr[call.from_user.id]['pointA'] + ' - ' + dict_sotr[call.from_user.id]['pointB'] + ', \nвремя - ' + dict_sotr[call.from_user.id]['time'] + inf_car
            else:
                message = 'По маршруту: ' + dict_sotr[call.from_user.id]['pointA'] + ' - ' + dict_sotr[call.from_user.id]['pointB'] + ', \nвремя - ' + dict_sotr[call.from_user.id]['time'] + ', \nпромежуточная точка ' + str(dict_sotr[call.from_user.id]['dopPoint']) + inf_car
        else:
            message = ''

        index_user = 0
        if call.data == 'false':
            for i in spisok_reg:
                name = spisok_reg[i]['name']
                if call.message.text[30:] == name:
                    index_user = i
           
            if call.from_user.id in dict_sotr:
                if dict_sotr[call.from_user.id]['type'] == 'driver':
                    if call.from_user.id in book:
                    # for j in book:
                        # for r in j:
                        # if int(j) == call.from_user.id:
                        bot.send_message(index_user, spisok_reg[call.from_user.id]['name'] + ' с вами не сможет поехать')
                        bot.send_message(call.from_user.id, 'Отказано')
                if dict_sotr[call.from_user.id]['type'] == 'passenger':
                    if index_user in book:
                        for j in book[index_user]:
                            # for r in j:
                            if int(j) == call.from_user.id:
                                bot.send_message(index_user, spisok_reg[call.from_user.id]['name'] + ' с вами не сможет поехать')
                                bot.send_message(int(j), 'Отказано')

        elif int(call.data) in spisok_reg:
            if dict_sotr[call.from_user.id]['type'] == 'driver':
                if int(call.data) in passenger_bron:
                    if passenger_bron[int(call.data)] == True:
                        # bot.send_message(call.from_user.id, 'Вы забронировали поездку, вам нужно завершить текущую поездку.')
                        bot.send_message(call.from_user.id, 'Пользователь ' + spisok_reg[int(call.data)][
                                        'name'] + ' уже едет с другим водителем, вам необходимо посмотреть другие заявки для вашего маршрута')
                        return
               
            elif dict_sotr[call.from_user.id]['type'] == 'passenger':
                if call.from_user.id in passenger_bron:
                    if passenger_bron[call.from_user.id] == True:
                        bot.send_message(call.from_user.id, 'Вы забронировали поездку, вам нужно завершить текущую поездку.')
                        return

            if int(call.data) in dict_sotr:
                typeUser = dict_sotr[call.from_user.id]['type']
                if typeUser == 'driver':
                    if call.from_user.id in book:
                        book[int(call.from_user.id)][int(call.data)] = True
                    else:
                        book[int(call.from_user.id)] = {int(call.data): True}
                    # book[int(call.from_user.id)] = [{int(call.data): True}]
                    passenger_bron[int(call.data)] = True
                    if call.from_user.id in driver_number:
                        num_driver = driver_number[call.from_user.id]
                        driver_number[call.from_user.id] = num_driver + 1
                elif typeUser == 'passenger':
                    if int(call.data) in book:
                        book[int(call.data)][int(call.from_user.id)] = True
                    else:
                        book[int(call.data)] = {int(call.from_user.id): True}
                    passenger_bron[call.from_user.id] = True
                    if int(call.data) in driver_number:
                        num_driver = driver_number[int(call.data)]
                        driver_number[int(call.data)] = num_driver + 1


                bot.send_message(int(call.data), 'С вами поедет ' + spisok_reg[call.from_user.id]['name'])
                bot.send_message(int(call.data), message)
                bot.send_message(int(call.data), spisok_reg[call.from_user.id]['tel'] + " - телефон для связи")
                if not spisok_reg[call.from_user.id]['username'] == None:
                    bot.send_message(int(call.data),  "@" +spisok_reg[call.from_user.id]['username'] + " - чтобы написать сообщение, нажмите на имя пользователя и выберите иконку чата рядом с аватаром пользователя")
                bot.send_message(call.from_user.id, 'С вами поедет ' + spisok_reg[int(call.data)]['name'])
                bot.send_message(call.from_user.id, spisok_reg[int(call.data)]['tel'] + " - телефон для связи")

                # markup2 = telebot.types.InlineKeyboardMarkup()
                # inlineButton2 = telebot.types.InlineKeyboardButton(text='Потвердить', switch_inline_query_current_chat="@" +spisok_reg[int(call.data)]['username'])
                # markup2.row(inlineButton2)
                driver = spisok_reg[int(call.data)]['name']
                passenger = spisok_reg[call.from_user.id]['name']
                # f = open('poezdki_plus.txt', 'a')
                # f.write('\n ' + driver + ' поехал(а) с ' + passenger + ' в ' +str(datetime.datetime.now()) +"; ")
                # f.close()

                if not spisok_reg[int(call.data)]['username'] == None:
                    bot.send_message(call.from_user.id,  "@" +spisok_reg[int(call.data)]['username'] + " - чтобы написать сообщение, нажмите на имя пользователя и выберите иконку чата рядом с аватаром пользователя")
                with open('booked.txt', 'a') as f:
                    json.dump(book, f)
    else:
        bot.send_message(call.from_user.id, 'Вы не создали маршрут')


@bot.callback_query_handler(func=lambda call: call.from_user.id in spisok_reg)
def callback_user(call):
    if int(call.data) in spisok_reg:
        if call.from_user.id in dict_sotr:
            if dict_sotr[call.from_user.id]['type'] == 'driver':
                if driver_num_passenger[call.from_user.id] <= driver_number[call.from_user.id]:
                    bot.send_message(call.from_user.id, 'У вас заполнена машина, количество пассажиров переполнено')
                    return
            elif dict_sotr[call.from_user.id]['type'] == 'passenger':
                if driver_num_passenger[int(call.data)] <= driver_number[int(call.data)]:
                    bot.send_message(call.from_user.id, 'У водителя машина заполнена, вам нужно посмотреть других водителей')
                    return

            if dict_sotr[call.from_user.id]['type'] == 'driver':
                if int(call.data) in passenger_bron:
                    if passenger_bron[int(call.data)] == True:
                        # bot.send_message(call.from_user.id, 'Вы забронировали поездку, вам нужно завершить текущую поездку.')
                        bot.send_message(call.from_user.id, 'Пользователь ' + spisok_reg[int(call.data)][
                                        'name'] + ' уже едет с другим водителем, вам необходимо посмотреть другие заявки для вашего маршрута')
                        return
            elif dict_sotr[call.from_user.id]['type'] == 'passenger':
                for i in book:
                    if call.from_user.id in book[i]:
                        if book[i][call.from_user.id] == True:
                            # bot.send_message(int(call.data), 'Пользователь ' + spisok_reg[call.from_user.id][
                            #     'name'] + ' уже едет с другим водителем, вам необходимо посмотреть другие заявки для вашего маршрута')
                            bot.send_message(call.from_user.id, 'Вы уже едите вместе с ' + spisok_reg[i]['name'])
                            return

            name = spisok_reg[int(call.data)]['name']
            if call.from_user.id in dict_sotr:
                # for m in dict_sotr[call.from_user.id]:
                if 'infocar' in dict_sotr[call.from_user.id]:
                    inf_car = ', машина ' + dict_sotr[call.from_user.id]['infocar']
                else:
                    inf_car = ''
                if dict_sotr[call.from_user.id]['dopPoint'] == []:
                    message = 'По маршруту: ' + dict_sotr[call.from_user.id]['pointA'] + ' - ' + dict_sotr[call.from_user.id]['pointB'] + ', \nвремя - ' + dict_sotr[call.from_user.id]['time'] + inf_car
                else:
                    message = 'По маршруту: ' + dict_sotr[call.from_user.id]['pointA'] + ' - ' + dict_sotr[call.from_user.id]['pointB'] + ', \nвремя - ' + dict_sotr[call.from_user.id]['time'] + ', \nпромежуточная точка ' + str(dict_sotr[call.from_user.id]['dopPoint']) + inf_car
            else:
                message = ''

            # message = 'По маршруту: ' + third_param + ' - ' + four_param + ', \nвремя - ' + five_param + ', \nпромежуточная точка ' + six_param
            if int(call.data) in dict_sotr:
                typeUser = dict_sotr[call.from_user.id]['type']
                if typeUser == 'driver':
                    if call.from_user.id in book:
                        book[int(call.from_user.id)][int(call.data)] = False
                    else:
                        book[int(call.from_user.id)] = {int(call.data): False}
                elif typeUser == 'passenger':
                    if int(call.data) in book:
                        book[int(call.data)][int(call.from_user.id)] = False
                    else:
                        book[int(call.data)] = {int(call.from_user.id): False}
                    # book[int(call.data)] = [{int(call.from_user.id): False}]
                markup2 = telebot.types.InlineKeyboardMarkup()
                inlineButton2 = telebot.types.InlineKeyboardButton(text='Подтвердить', callback_data=int(call.from_user.id))
                inlineButton3 = telebot.types.InlineKeyboardButton(text='Отказать', callback_data='false')
                markup2.row(inlineButton2, inlineButton3)

                bot.send_message(int(call.data),message)
                bot.send_message(int(call.data), 'Вам предлагает поехать вместе ' + spisok_reg[call.message.chat.id]['name'], reply_markup=markup2)
                bot.send_message(call.from_user.id, 'Уведомление отправлено, дождитесь подтверждения. ' + name + ' подтвердит поездку.')
            else:
                bot.send_message(call.from_user.id, 'К сожалению, пользователь отменил поездку.')
        else:
            bot.send_message(call.from_user.id, 'Вы не создали маршрут')




def del_dict(user_id):
    if user_id in dict_sotr:
        m = 0
        markup1 = telebot.types.InlineKeyboardMarkup()
        inlineButton2 = telebot.types.InlineKeyboardButton(text='Удалить маршрут', callback_data=str(m))
        markup1.row(inlineButton2)
        bot.send_message(user_id, 'Информация о времени ' + dict_sotr[user_id]['time'] + ', по маршруту ' + dict_sotr[user_id]['pointA'] + ' - ' + dict_sotr[user_id]['pointB'] + ', промежуток: ' + str(dict_sotr[user_id]['dopPoint']))
        bot.send_message(user_id, "Удалить маршрут", reply_markup=markup1)
        m +=1

def find_me(user_id, d):
    with open('spisok_register.txt', 'r') as f:
        try:
            spisok_zareg = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            spisok_zareg = {}
    bot.send_message(user_id, 'Ожидайте уведомления по маршрутам', reply_markup=keyboard_main)
    if user_id in dict_sotr:
        for i in dict_sotr:
            if i == user_id:
                continue
            elif i != user_id:
                # for j in dict_sotr[i]:
                if dict_sotr[i]['type'] == d['type']:
                    continue
                else:
                    # if dict_sotr[i]['pointA'] == d['pointA'] or dict_sotr[i]['pointB'] == d['pointB'] or dict_sotr[i]['time'] == d['time'] or dict_sotr[i]['dopPoint'] == d['dopPoint']:
                    if 'infocar' in dict_sotr[i]:
                        inf_car = ', машина ' + dict_sotr[i]['infocar']
                    else:
                        inf_car = ''

                    if dict_sotr[i]['dopPoint'] == []:
                        message = 'По маршруту: ' + dict_sotr[i]['pointA'] + ' - ' + dict_sotr[i]['pointB'] + ', \nвремя - ' + dict_sotr[i]['time'] + inf_car
                    else:
                        message = 'По маршруту: ' + dict_sotr[i]['pointA'] + ' - ' + dict_sotr[i]['pointB'] + ', \nвремя - ' + dict_sotr[i]['time'] + ', \nпромежуточная точка ' + str(dict_sotr[i]['dopPoint']) + inf_car
                    bot.send_message(user_id, 'Актуальные заявки')
                    # bot.send_message(user_id, message)
                    if i in spisok_reg:
                        imya_polz = imena(spisok_reg[i]['name'])
                        bot.send_message(user_id, imya_polz)
                    elif str(i) in spisok_zareg:
                        imya_polz = imena(spisok_zareg[str(i)]['name'])
                        bot.send_message(user_id, imya_polz)
                    markup1 = telebot.types.InlineKeyboardMarkup()
                    s = str(i) + '|' + d['type'] + '|' + d['pointA'] + '|' + d['pointB'] + '|' + d['time'] + '|' + str(d['dopPoint'])
                    inlineButton2 = telebot.types.InlineKeyboardButton(text='Поехать вместе', callback_data=i)
                    markup1.row(inlineButton2)
                    bot.send_message(user_id, message, reply_markup=markup1)
                    
def push_msg(user_id, d):
    with open('spisok_register.txt', 'r') as f:
        try:
            spisok_zareg = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            spisok_zareg = {}

    if user_id in dict_sotr:
        # for i in dict_sotr:
        for i in list(dict_sotr.keys()):
            if i == user_id:
                continue
            elif i != user_id:
                # for j in dict_sotr[i]:
                if dict_sotr[i]['type'] == d['type']:
                    continue
                else:
                    if 'infocar' in d:
                        inf_car = ', машина ' + d['infocar']
                    else:
                        inf_car = ''

                    if d['dopPoint'] == []:
                        message = 'По маршруту: ' + d['pointA'] + ' - ' + d['pointB'] + ', \nвремя - ' + d['time'] +  inf_car
                    else:
                        message = 'По маршруту: ' + d['pointA'] + ' - ' + d['pointB'] + ', \nвремя - ' + d['time'] + ', \nпромежуточная точка ' + str(d['dopPoint']) +  inf_car
                    bot.send_message(i, 'Актуальные заявки')
                   
                    if user_id in spisok_reg:
                        imya_polz = imena(spisok_reg[user_id]['name'])
                        bot.send_message(i, imya_polz)
                    elif str(user_id) in spisok_zareg:
                        imya_polz = imena(spisok_zareg[str(user_id)]['name'])
                        bot.send_message(i, imya_polz)
                    markup1 = telebot.types.InlineKeyboardMarkup()
                    inlineButton2 = telebot.types.InlineKeyboardButton(text='Поехать вместе', callback_data=user_id)
                    markup1.row(inlineButton2)
                    bot.send_message(i, message, reply_markup=markup1)
                   

def proverka_registracii(user_id):
    with open('spisok_register.txt', 'r') as f:
        try:
            spisok_reg = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            spisok_reg = {}
    if user_id in spisok_reg:
        return True
    else:
        return False

def imena(str_imen):
    imya = str_imen.split(' ')
    return imya[1]


@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.chat.id, 'Зарегистрируйтесь для пользования сервисом.', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global user_type, dict_sotr, dict_poputi, spisok_reg

    if message.text.lower() == 'регистрация':
        bot.send_message(message.from_user.id, "Укажите ваше ФИО для регистрации")
        bot.register_next_step_handler(message, ads_fio)

    elif message.text.lower() == 'хочу поехать':

        with open('spisok_register.txt', 'r') as f:
            try:
                spisok_zareg = json.load(f)
            # if the file is empty the ValueError will be thrown
            except ValueError:
                spisok_zareg = {}
        if message.from_user.id in book:
            del book[message.from_user.id]

        delete = {}
        for key in book:
            for i in book[key]:
                if i == int(message.from_user.id):
                    delete[key] = i
        if delete != {}:
            for i, j in delete.items():
                del book[i][j]

        if message.from_user.id in passenger_bron:
            passenger_bron[message.from_user.id] = False

        if message.from_user.id in spisok_reg:
            if spisok_reg[message.from_user.id]['username'] == None:
                if message.from_user.username != None:
                    spisok_reg[message.from_user.id]['username'] = message.from_user.username
                else:
                    bot.send_message(message.from_user.id, "В настройках заполните ИМЯ ПОЛЬЗОВАТЕЛЯ, чтобы с вами могли связаться")
                    video = open('instruction.mp4', 'rb')
                    bot.send_video(message.from_user.id, video)
            else:
                bot.send_message(message.from_user.id, 'Вы сегодня Водитель или Пассажир?', reply_markup=keyboard_step)
        elif str(message.from_user.id) in spisok_zareg:
            spisok_reg[message.from_user.id] = spisok_zareg.pop(str(message.from_user.id))
            if spisok_reg[message.from_user.id]['username'] == None:
                if message.from_user.username != None:
                    spisok_reg[message.from_user.id]['username'] = message.from_user.username
                else:
                    bot.send_message(message.from_user.id, "В настройках заполните ИМЯ ПОЛЬЗОВАТЕЛЯ, чтобы с вами могли связаться")
                    video = open('instruction.mp4', 'rb')
                    bot.send_video(message.from_user.id, video)
            else:
                bot.send_message(message.from_user.id, 'Вы сегодня Водитель или Пассажир?', reply_markup=keyboard_step)

        else:
            result_reg = proverka_registracii(message.from_user.id)
            # bot.register_next_step_handler(message, ads_fio)
            if not result_reg:
                bot.send_message(message.from_user.id, "Необходимо пройти процедуру регистрации. Введите /start")

    elif message.text.lower() == 'поездка успешно завершена':
        doc = open('history.txt', 'a')
        name = spisok_reg[message.from_user.id]['name']
        typeUser = dict_sotr[message.from_user.id]['type']
        mark_msg = False
        if typeUser == 'driver':
            if message.from_user.id in book:
                history_driver = book[message.from_user.id]
                namePassengers = []
                mark_msg = True
                for m in history_driver:
                    # n = list(m)[0]
                    if history_driver[m] == True:
                        nameP = spisok_reg[m]['name']
                        mark_msg = True
                        namePassengers.append(nameP)
                        doc.write('\n ' + name + ' как ' + typeUser + ' поехал(а) с ' + str(namePassengers)+ ' в ' +str(datetime.datetime.now()) +"; ")
                # del book[message.from_user.id]
        elif typeUser == 'passenger':
            # passenger_bron[message.from_user.id] = False
            mark_msg = True
            for i in book:
                for j in book[i]:
                    if message.from_user.id == j:
                        # history_passenger = i[message.from_user.id]
                        if book[i][j] == True:
                            # mark_msg = True
                            nameP = spisok_reg[i]['name']
                            doc.write('\n ' + name + ' как ' + typeUser + ' поехал(а) с ' + nameP + ' в ' +str(datetime.datetime.now()) +"; ")

        doc.close()
        del dict_sotr[message.from_user.id]

        # bot.send_message(message.from_user.id, 'Спасибо за то, что возпользовались сервисом, будем делать вам новых успешных поездок!', reply_markup=keyboard_start)
        if mark_msg:
            bot.send_message(message.from_user.id,
                         'Оцените вашу поездку',
                         reply_markup=key_market)
            bot.register_next_step_handler(message, market_bot)
        else:
            bot.send_message(message.from_user.id,
                             'Спасибо за то, что возпользовались сервисом, будем делать вам новых успешных поездок!',
                             reply_markup=keyboard_start)

    elif message.text.lower() == 'водитель':
        user_type = 'driver'
        dict_poputi[message.from_user.id] = {'type':user_type}
        bot.send_message(message.from_user.id, 'Откуда поедем?', reply_markup=keyboard_stop)
        bot.register_next_step_handler(message, ads_pointA)

    elif message.text.lower() == 'пассажир':
        user_type = 'passenger'
        dict_poputi[message.from_user.id] = {'type': user_type}
        bot.send_message(message.from_user.id, 'Откуда поедем?', reply_markup=keyboard_stop)
        bot.register_next_step_handler(message, ads_pointA)

    elif message.text.lower() == 'другое время':
        bot.send_message(message.from_user.id, 'Укажите время поездки', reply_markup=keyboard_stop)

    elif message.text.lower() == 'добавить еще промежуточную остановку':
        bot.send_message(message.from_user.id, 'Укажите еще промежуточную остановку', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, ads_pointC)

    elif message.text.lower() == 'пропустить':       
        d = dict_poputi[message.from_user.id]       
        dict_sotr[message.from_user.id] = dict_poputi[message.from_user.id]
        push_msg(message.from_user.id, d)
        find_me(message.from_user.id, d)
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_main)
    elif message.text.lower() == 'завершить ввод маршрута':
       
        with open('user_marshrut.txt', 'a') as f:
            json.dump(dict_poputi, f)
        d = dict_poputi[message.from_user.id]
        
        dict_sotr[message.from_user.id] = dict_poputi[message.from_user.id]
        push_msg(message.from_user.id, d)
        find_me(message.from_user.id, d)
        # bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_main)

    elif message.text.lower() == 'остановить поиск':
        del dict_poputi[message.from_user.id]
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_start)
    elif message.text.lower() == 'найти попутчика':
        find_me(message.from_user.id)

    elif message.text.lower() == 'отменить поездку':
        del_dict(message.from_user.id)

    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Введите /start")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

@bot.message_handler(content_types=['text'])
def ads_fio(message):
    fio = message.text
    probel = fio.count(' ')
    if probel >= 2:
        spisok_reg[message.from_user.id] = {'name': message.text}
        bot.send_message(message.from_user.id, "Укажите ваш номер телефона, начиная +7 или 8")
        bot.register_next_step_handler(message, ads_tel)
    else:
        bot.send_message(message.from_user.id, "Укажите ваш ФИО, в формате Иванов Иван Иванович")
        bot.register_next_step_handler(message, ads_fio)


@bot.message_handler(content_types=['text'])
def ads_tel(message):

    try:
        num_tel = int(message.text)
        a = list(str(num_tel))
        if isinstance(num_tel, int) and len(a) == 11:
            spisok_reg[message.from_user.id]['tel'] = message.text.lower()
            spisok_reg[message.from_user.id]['username'] = message.from_user.username
            with open('spisok_register.txt', 'w') as f:
                json.dump(spisok_reg, f)
            bot.send_message(message.from_user.id, "Вы успешно зарегистрировались!", reply_markup=keyboard_start)
        else:
            bot.send_message(message.from_user.id,
                             'Вы указали неверный формат номера телефона. Укажите 11 символов номера телефона, начиная с +7 или 8. Введите номер телефона повторно.')
            bot.register_next_step_handler(message, ads_tel)
    except:
        bot.send_message(message.from_user.id,
                         'Вы указали неверный формат номера телефона. Введите номер телефона повторно.')
        bot.register_next_step_handler(message, ads_tel)


@bot.message_handler(content_types=['text'])
def ads_pointA(message):
    if message.text.lower() == 'остановить поиск':
        del dict_poputi[message.from_user.id]
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_start)
    else:
        dict_poputi[message.from_user.id]['pointA'] = message.text.lower()
        bot.send_message(message.from_user.id, 'Куда поедем?', reply_markup=keyboard_stop)
        bot.register_next_step_handler(message, ads_pointB)

@bot.message_handler(content_types=['text'])
def ads_pointB(message):
    if message.text.lower() == 'остановить поиск':
        del dict_poputi[message.from_user.id]
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_start)
    else:
        dict_poputi[message.from_user.id]['pointB'] = message.text.lower()
        bot.send_message(message.from_user.id, 'Выберите время поездки?', reply_markup=key_time)
        bot.register_next_step_handler(message, ads_time)

@bot.message_handler(content_types=['text'])
def ads_time(message):
    if message.text.lower() == 'остановить поиск':
        del dict_poputi[message.from_user.id]
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_start)
    elif message.text.lower() == 'другое время':
        bot.send_message(message.from_user.id, 'Укажите время поездки, в формате 00:00', reply_markup=keyboard_stop)
        bot.register_next_step_handler(message, ads_time)

    else:
        dict_poputi[message.from_user.id]['time'] = message.text.lower()
        dict_poputi[message.from_user.id]['dopPoint'] = []
        
        if dict_poputi[message.from_user.id]['type'] == 'driver':
            bot.send_message(message.from_user.id, 'Укажите марку автомобиля, цвет и гос. номер', reply_markup=keyboard_stop)
            bot.register_next_step_handler(message, ads_infocar)
        elif dict_poputi[message.from_user.id]['type'] == 'passenger':
            bot.send_message(message.from_user.id, 'Укажите промежуточную остановку', reply_markup=key_dopost)
            bot.register_next_step_handler(message, ads_pointC)


@bot.message_handler(content_types=['text'])
def ads_pointC(message):
    if message.text.lower() == 'остановить поиск':
        del dict_poputi[message.from_user.id]
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_start)
    elif message.text.lower() == 'пропустить':
       
        with open('user_marshrut.txt', 'a') as f:
            json.dump(dict_poputi, f)
        d = dict_poputi[message.from_user.id]
       
        dict_sotr[message.from_user.id] = dict_poputi[message.from_user.id]
        push_msg(message.from_user.id, d)
        find_me(message.from_user.id, d)
        # bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_main)
    else:
        dict_poputi[message.from_user.id]['dopPoint'].append(message.text.lower())
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=key_point)

@bot.message_handler(content_types=['text'])
def ads_infocar(message):
    if message.text.lower() == 'остановить поиск':
        del dict_poputi[message.from_user.id]
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_start)
    else:
        dict_poputi[message.from_user.id]['infocar'] = message.text.lower()
        bot.send_message(message.from_user.id, 'Укажите количество пассажиров, которых возьмете в дорогу', reply_markup=key_num)
        bot.register_next_step_handler(message, ads_num_passenger)

@bot.message_handler(content_types=['text'])
def ads_num_passenger(message):
    if message.text.lower() == 'остановить поиск':
        del dict_poputi[message.from_user.id]
        bot.send_message(message.from_user.id, 'Выберите следующее', reply_markup=keyboard_start)
    else:
        num_passenger = message.text.lower()
        driver_num_passenger[message.from_user.id] = int(num_passenger)
        driver_number[message.from_user.id] = 0
        bot.send_message(message.from_user.id, 'Укажите промежуточную остановку', reply_markup=key_dopost)
        bot.register_next_step_handler(message, ads_pointC)

@bot.message_handler(content_types=['text'])
def market_bot(message):
    botMark[message.from_user.id] = message.text.lower()
    with open('mark_user.txt', 'a') as f:
        json.dump(botMark, f)
    bot.send_message(message.from_user.id,
                     'Спасибо за то, что воспользовались сервисом, будем делать вам новых успешных поездок!',
                     reply_markup=keyboard_start)

# bot.skip_pending = True

bot.polling(none_stop=True, interval=0, timeout=30)
