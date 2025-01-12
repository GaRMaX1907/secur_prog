from logic import DB_Manager
from logicCOURSE import Course
from logicWEATHER import Weather

from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types
import random

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 

cancel_button = "Отмена 🚫"
def cansel(message):
    bot.send_message(message.chat.id, "Чтобы посмотреть команды, используй - /info", reply_markup=hideBoard)
  
def no_tasks(message):
    bot.send_message(message.chat.id, 'У тебя пока нет планов и задач!\nМожешь добавить их с помошью команды /new_task')

def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(row, callback_data=row))
    return markup

def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
        markup.add(KeyboardButton(cancel_button))
    return markup

attributes_of_tasks = {'Название задачи' : ["Введите название задачи", "task_name"],
                          "Описание" : ["Введите содержание задачи", "description"],
                          "Ссылка" : ["Введите ссылку для задачи (если нужно)", "url"],
                          "Статус" : ["Выберите новый статус для задачи", "status_id"]}

def info_task(message, user_id, task_name):
    info = manager.get_task_info(user_id, task_name)[0]
    timestatuses = manager.get_task_timestatuses(task_name)
    if not timestatuses:
        timestatuses = 'Статус времени пока не добавлен'
    bot.send_message(message.chat.id, f"""task name: {info[0]}
Description: {info[1]}
Link: {info[2]}
Status: {info[3]}
timestatuses: {timestatuses}
""")

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """Привет! Я твой личный бот-секретарь
Помогу составить планы на день, определиться с выбором; покажу актуальный курс доллара и погоду в твоём городе!
Также можешь обратиться за помощью к Gigachat) 
""")
    info(message)
    
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
"""
Вот команды которые могут тебе помочь:

/new_task - используй для добавления новой задачи
/dollar - просматривай актуальный курс доллара
/weather - просматривай актуальную погоду
/random - подбрось монетку для того, чтобы определиться с выбором или развлечь себя


Также ты можешь ввести название задачи и узнать информацию о ней!""")
    
#Дополнительные функции

@bot.message_handler(command=['/random'])
def random_handler(message):
    bot.send_message(message.chat.id, random('Орёл', 'Решка'))

@bot.message_handler(command=['dollar'])
def dollar_handler(messsage):
    get_course_dol = Course
    bot.send_message(messsage.chat.id, get_course_dol)

@bot.message_handler(command=['weather'])
def wether_handler(message):
    get_weather = Weather
    bot.send_message(message.chat.id, get_weather)

@bot.message_handler(command=['chatGPT'])
def chatGPT_handler(message):
    get_gpt = Gigachat
    bot.send_message(message.chat.id, get_gpt)
    
#Функция "Новая задача" 

@bot.message_handler(commands=['new_task'])
def addtask_command(message):
    bot.send_message(message.chat.id, "Введите название задачи:")
    bot.register_next_step_handler(message, name_task)

def name_task(message):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, "Введите текст задачи")
    bot.register_next_step_handler(message, description_task, data=data)

def description_task(message, data):
    data.append(message.text)
    bot.send_message(message.chat.id, "Введите ссылку на что-либо (если требует задача)")
    bot.register_next_step_handler(message, link_task, data=data)

def link_task(message, data):
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()] 
    bot.send_message(message.chat.id, "Введите текущий статус проекта", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, callback_task, data=data, statuses=statuses)


def callback_task(message, data, statuses):
    status = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if status not in statuses:
        bot.send_message(message.chat.id, "Ты выбрал статус не из списка, попробуй еще раз!)", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_task, data=data, statuses=statuses)
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_task([tuple(data)])
    bot.send_message(message.chat.id, "Задача сохранена")

#Функция изменнения временного промежутка

@bot.message_handler(commands=['timestatuses'])
def timestatus_handler(message):
    user_id = message.from_user.id
    tasks = manager.get_tasks(user_id)
    if tasks:
        tasks = [x[2] for x in tasks]
        bot.send_message(message.chat.id, 'Выберите задачу для которой нужно выбрать статус времени', reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, timestatus_task, tasks=tasks)
    else:
        no_tasks(message)


def timestatus_task(message, tasks):
    task_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
        
    if task_name not in tasks:
        bot.send_message(message.chat.id, 'У тебя нет такой задачи, попробуйте еще раз!) Выбери задачу для которого нужно выбрать временной статус', reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, timestatus_task, tasks=tasks)
    else:
        timestatuses = [x[1] for x in manager.get_timestatuses()]
        bot.send_message(message.chat.id, 'Выберите статус времени', reply_markup=gen_markup(timestatuses))
        bot.register_next_step_handler(message, set_timestatus, task_name=task_name, timestatuses=timestatuses)

def set_timestatus(message, task_name, timestatuses):
    timestatus = message.text
    user_id = message.from_user.id
    if message.text == cancel_button:
        cansel(message)
        return
        
    if timestatus not in timestatuses:
        bot.send_message(message.chat.id, 'Видимо, вы выбрал временной статус не из спика, попробуй еще раз!) Выберите параметр времени для задачи', reply_markup=gen_markup(timestatuses))
        bot.register_next_step_handler(message, set_timestatus, task_name=task_name, timestatuses=timestatuses)
        return
    manager.insert_timestatus(user_id, task_name, timestatus )
    bot.send_message(message.chat.id, f'Временной промежуток {timestatus} добавлен проекту {task_name}')

#Функция показа задач

@bot.message_handler(commands=['tasks'])
def get_tasks(message):
    user_id = message.from_user.id
    tasks = manager.get_tasks(user_id)
    if tasks:
        text = "\n".join([f"task name:{x[2]} \nLink:{x[4]}\n" for x in tasks])
        bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in tasks]))
    else:
        no_tasks(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    task_name = call.data
    info_task(call.message, call.from_user.id, task_name)

#Функиция удаления

@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    tasks = manager.get_tasks(user_id)
    if tasks:
        text = "\n".join([f"task name:{x[2]} \nLink:{x[4]}\n" for x in tasks])
        tasks = [x[2] for x in tasks]
        bot.send_message(message.chat.id, text, reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, delete_task, tasks=tasks)
    else:
        no_tasks(message)

def delete_task(message, tasks):
    task = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cansel(message)
        return
    if task not in tasks:
        bot.send_message(message.chat.id, 'У тебя нет такой задачи, попробуйе выбрать еще раз!', reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, delete_task, tasks=tasks)
        return
    task_id = manager.get_task_id(task, user_id)
    manager.delete_task(user_id, task_id)
    bot.send_message(message.chat.id, f'Задача {task} удалена!')

#Функция изменения конкретной задачи

@bot.message_handler(commands=['update_tasks'])
def update_task(message):
    user_id = message.from_user.id
    tasks = manager.get_tasks(user_id)
    if tasks:
        tasks = [x[2] for x in tasks]
        bot.send_message(message.chat.id, "Выберите задачу, которую хотите изменить", reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, update_task_step_2, tasks=tasks )
    else:
        no_tasks(message)

def update_task_step_2(message, tasks):
    task_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if task_name not in tasks:
        bot.send_message(message.chat.id, "Что-то пошло не так!) Выберите проект, который хотите изменить еще раз:", reply_markup=gen_markup(tasks))
        bot.register_next_step_handler(message, update_task_step_2, tasks=tasks )
        return
    bot.send_message(message.chat.id, "Выбери, что требуется изменить в задаче", reply_markup=gen_markup(attributes_of_tasks.keys()))
    bot.register_next_step_handler(message, update_task_step_3, task_name=task_name)

def update_task_step_3(message, task_name):
    attribute = message.text
    reply_markup = None 
    if message.text == cancel_button:
        cansel(message)
        return
    if attribute not in attributes_of_tasks.keys():
        bot.send_message(message.chat.id, "Кажется, вы ошиблись, попробуйте еще раз!)", reply_markup=gen_markup(attributes_of_tasks.keys()))
        bot.register_next_step_handler(message, update_task_step_3, task_name=task_name)
        return
    elif attribute == "Статус":
        rows = manager.get_statuses()
        reply_markup=gen_markup([x[0] for x in rows])
    bot.send_message(message.chat.id, attributes_of_tasks[attribute][0], reply_markup = reply_markup)
    bot.register_next_step_handler(message, update_task_step_4, task_name=task_name, attribute=attributes_of_tasks[attribute][1])

def update_task_step_4(message, task_name, attribute): 
    update_info = message.text
    if attribute== "status_id":
        rows = manager.get_statuses()
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cansel(message)
        else:
            bot.send_message(message.chat.id, "Был выбран неверный статус, попробуй еще раз!)", reply_markup=gen_markup([x[0] for x in rows]))
            bot.register_next_step_handler(message, update_task_step_4, task_name=task_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = (update_info, task_name, user_id)
    manager.update_tasks(attribute, data)
    bot.send_message(message.chat.id, "Готово! Обновления внесены!)")


@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    tasks =[ x[2] for x in manager.get_tasks(user_id)]
    task = message.text
    if task in tasks:
        info_task(message, user_id, task)
        return
    bot.reply_to(message, "Нужна помощь?")
    info(message)

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()