from copy import deepcopy

from aiogram import Bot, Dispatcher, types
import sqlite3
import logging
import asyncio

import numpy as np
import scipy.linalg as sla

TOKEN = '5837099814:AAF-MZEKfbX3y8w2RxHNML9geT4wuv4N7dk'
bot = Bot(TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('base.db', check_same_thread=False)
cursor = conn.cursor()

#########################################
# Клавиатура для старта
keyboard_base = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                          one_time_keyboard=False, row_width=2)
keyboard_base.add('LinAl', 'Что ты можешь?', 'Закончить первый курс')

keyboard_linal = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                           one_time_keyboard=False,
                                           row_width=2)
keyboard_linal.add('T', 'Решить СЛУ', 'det', 'Назад')

keyboard_back = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                          one_time_keyboard=False, row_width=1)
keyboard_back.add('Назад')


#########################################

# 0 - main
# 1 - linal
# 11 - linal.T
# 12 - linal.det
# 13 - linal.SLU
def db_table_activity(user_id: int, activity_id: int, call_type: str):
    if call_type == "add":
        cursor.execute(
            'INSERT INTO activity_bd (user_id, Activity_id) VALUES (?, ?)',
            (user_id, activity_id))
    elif call_type == "change":
        cursor.execute(
            'UPDATE activity_bd SET Activity_id = ? WHERE user_id = ?',
            (activity_id, user_id))
    conn.commit()


def convert_str_to_array(matrix_str, X):
    arr = []
    for val in matrix_str.split(" "):
        if not val.isdigit():
            n = len(val.split("\n"))
            i = 1
            for sub_val in val.split("\n"):
                if not sub_val.isdigit():
                    return 1
                arr.append(int(sub_val))
                if i != n:
                    if X and len(X[-1]) != len(arr):
                        return 1
                    X.append(deepcopy(arr))
                    arr.clear()
                i += 1
        else:
            arr.append(int(val))

    if arr:
        if X and len(X[-1]) != len(arr):
            return 1
        X.append(deepcopy(arr))

    return 0


def covert_array_to_str(arr):
    result_str = ""
    for sub_arr in arr:
        for val in sub_arr:
            result_str += str(val) + " "
        result_str = result_str[:-1]
        result_str += "\n"
    return result_str


@dp.message_handler(commands=['start'])
async def hello_message(message):
    already_login = False
    act_id = 0
    for user in cursor.execute("SELECT user_id, Activity_id FROM activity_bd"):
        if user[0] == message.from_user.id:
            already_login = True
            act_id = user[1]
            break

    if already_login:
        if act_id == 0:
            keyboard = keyboard_base
        elif act_id == 1:
            keyboard = keyboard_linal
        else:
            db_table_activity(user_id=message.from_user.id, activity_id=0,
                              call_type="change")
            keyboard = keyboard_base
        await bot.send_message(message.from_user.id,
                               "Хай прив! Я твой помощник на этот первый курс, и кажется я тебя где-то видел! )00)",
                               reply_markup=keyboard)
    else:
        db_table_activity(user_id=message.from_user.id, activity_id=0,
                          call_type="add")
        await bot.send_message(message.from_user.id,
                               "Хай прив! Я твой помощник на этот первый курс! )00)",
                               reply_markup=keyboard_base)


@dp.message_handler(content_types=['text'])
async def get_text_messages(message):
    try:
        cursor.execute("SELECT Activity_id FROM activity_bd WHERE user_id = ?",
                       (message.from_user.id,))
        activity_id = cursor.fetchall()[0][0]
    except IndexError:
        await bot.send_message(message.from_user.id,
                               "Я с тобой не знаком, а с незнакомцами я не разговариваю(\n "
                               "напиши /start, чтобы мы смогли дружить",
                               reply_markup=keyboard_base)
        return

    bad_words = ['лох', 'дурак', 'чмо', 'идиот', 'хуй', 'ты хуй']
    if message.text in bad_words:
        await bot.send_message(message.from_user.id, "Сам " + message.text)
        return

    if activity_id == 0:
        if message.text == "LinAl":
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id, "Полиналим немного)",
                                   reply_markup=keyboard_linal)
            await bot.send_sticker(message.from_user.id,
                                   "CAACAgIAAxkBAAEG3ahjneqdU2w8QgI5Np0LeZRj8z-2aAACRwwAAl12OUld34pHbljmVCwE")
        elif message.text == "Что ты можешь?":
            await bot.send_message(message.from_user.id,
                                   "ооооо, я многое могу! Цель моя - помочь тебе на первом курсе)\n"
                                   "-могу полиналить с тобой:\n"
                                   "  @ транспонировать матричку;\n"
                                   "  @ определитель ее взять\n"
                                   "  @ решить СЛУшку прикольную\n",
                                   reply_markup=keyboard_base)
        elif message.text == "Закончить первый курс":
            cursor.execute("delete from activity_bd where user_id = ?",
                           (message.from_user.id,))
            conn.commit()
            await bot.send_message(message.from_user.id,
                                   "Надеюсь, я смог тебе помочь) Покеда!",
                                   reply_markup=keyboard_base)
        else:
            await bot.send_message(message.from_user.id,
                                   "Я не умею этого делать:(")
    elif activity_id == 1:
        if message.text == "T":
            db_table_activity(user_id=message.from_user.id, activity_id=11,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Введи матричку свою, что хочешь транспонировать",
                                   reply_markup=keyboard_back)
        elif message.text == "det":
            db_table_activity(user_id=message.from_user.id, activity_id=12,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Введи матричку свою, у которой определитель хочешь взять (напомню, она должна быть квадратной)",
                                   reply_markup=keyboard_back)
        elif message.text == "Решить СЛУ":
            db_table_activity(user_id=message.from_user.id, activity_id=13,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "СЛУ вот такое A|B, введи сначала матричку А, а потом матричку В "
                                   "(я воспринимаю все буквально, пишешь строчку - я ее читаю как строчку, пишешь столбик - для меня он столбик)",
                                   reply_markup=keyboard_back)
        elif message.text == "Назад":
            db_table_activity(user_id=message.from_user.id, activity_id=0,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Ну вернемся мы куда-то назад)",
                                   reply_markup=keyboard_base)
        else:
            await bot.send_message(message.from_user.id,
                                   "Я не умею этого делать:(")
    elif activity_id == 11:
        if message.text == "Назад":
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Ну вернемся мы куда-то назад)",
                                   reply_markup=keyboard_linal)
            return

        X = []
        result_str = ""
        log = convert_str_to_array(message.text, X)
        X = np.array(X)
        if log == 1:
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Это что такое? Фу, это не число, такое я не ем",
                                   reply_markup=keyboard_linal)
            return
        X = X.T
        result_str = covert_array_to_str(X)
        db_table_activity(user_id=message.from_user.id, activity_id=1,
                          call_type="change")
        await bot.send_message(message.from_user.id, result_str,
                               reply_markup=keyboard_linal)
    elif activity_id == 12:
        if message.text == "Назад":
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Ну вернемся мы куда-то назад)",
                                   reply_markup=keyboard_linal)
            return
        X = []
        result_str = ""
        log = convert_str_to_array(message.text, X)
        X = np.array(X)
        if log == 1:
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Это что такое? Фу, это не число, такое я не ем",
                                   reply_markup=keyboard_linal)
            return
        try:
            result_str = str(sla.det(X))
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id, result_str,
                                   reply_markup=keyboard_linal)
        except ValueError:
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Это что такое? Фу, я только квадратики ем!",
                                   reply_markup=keyboard_linal)
    elif activity_id == 13:
        if message.text == "Назад":
            db_table_activity(user_id=message.from_user.id, activity_id=1,
                              call_type="change")
            await bot.send_message(message.from_user.id,
                                   "Ну вернемся мы куда-то назад)",
                                   reply_markup=keyboard_linal)
            return
        cursor.execute("SELECT matrix_a FROM activity_bd WHERE user_id = ?",
                       (message.from_user.id,))
        matrix_a = cursor.fetchall()[0][0]
        if matrix_a == "NULL" or not matrix_a:
            cursor.execute(
                'UPDATE activity_bd SET matrix_a = ? WHERE user_id = ?',
                (message.text, message.from_user.id))
            conn.commit()
            await bot.send_message(message.from_user.id,
                                   "А теперь введи вторую",
                                   reply_markup=keyboard_back)
        else:
            A = []
            B = []
            result_str = ""
            log = convert_str_to_array(matrix_a, A)
            if log == 1:
                db_table_activity(user_id=message.from_user.id, activity_id=1,
                                  call_type="change")
                await bot.send_message(message.from_user.id,
                                       "Это что такое? Фу, это не число в первой матричке, такое я не ем",
                                       reply_markup=keyboard_linal)
                cursor.execute(
                    'UPDATE activity_bd SET matrix_a = ? WHERE user_id = ?',
                    ("NULL", message.from_user.id))
                conn.commit()
                return
            log = convert_str_to_array(message.text, B)
            B = np.array(B)
            if log == 1:
                db_table_activity(user_id=message.from_user.id, activity_id=1,
                                  call_type="change")
                await bot.send_message(message.from_user.id,
                                       "Это что такое? Фу, это не число во второй матричке, такое я не ем",
                                       reply_markup=keyboard_linal)
                cursor.execute(
                    'UPDATE activity_bd SET matrix_a = ? WHERE user_id = ?',
                    ("NULL", message.from_user.id))
                conn.commit()
                return
            try:
                X = sla.solve(A, B)
                result_str = covert_array_to_str(X)
                db_table_activity(user_id=message.from_user.id, activity_id=1,
                                  call_type="change")
                await bot.send_message(message.from_user.id, result_str,
                                       reply_markup=keyboard_linal)
            except ValueError:
                db_table_activity(user_id=message.from_user.id, activity_id=1,
                                  call_type="change")
                await bot.send_message(message.from_user.id,
                                       "Это что такое? Ты втираешь какую-то дичь!",
                                       reply_markup=keyboard_linal)
            finally:
                cursor.execute(
                    'UPDATE activity_bd SET matrix_a = ? WHERE user_id = ?',
                    ("NULL", message.from_user.id))
                conn.commit()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
