from aiogram import types, Router, Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config
from time import sleep
import os
import sys
from clientbase import PyroGRAMM
from states import SendMessage, AddAdmin, DeleteAdmin
from datetime import datetime, timedelta
from bd import BDRequests
from aiogram.filters.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback


bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
BD = BDRequests()
SCHEDULER = AsyncIOScheduler(timezone='Europe/Moscow')
SCHEDULER.start()

#PR = PyroGRAMM()

async def restore_tasks():
    BD.delete_old()
    all_tasks = BD.select_all()
    for task in all_tasks:
        job_id = SCHEDULER.add_job(send_post, trigger='date', kwargs={'text' : task[2], 'image_id' : task[3], 'sticker_id' : task[4]}, next_run_time=task[1]).id
        BD.update_job_id(task[0], job_id)


async def add_task(date, text, image_id, sticker_id):
    job_id = SCHEDULER.add_job(send_post, trigger='date', kwargs={'text' : text, 'image_id' : image_id, 'sticker_id' : sticker_id}, next_run_time=date).id
    print(job_id)
    BD.insert_task(date, text, image_id, sticker_id, job_id)

async def send_post(text, image_id, sticker_id):
    channels_id = config.CHANELLS_ID
    for channel in channels_id:
        try:
            if image_id != 'false':
                await bot.send_photo(channel, image_id, caption=text, parse_mode='html')
            elif sticker_id != 'false':
                await bot.send_sticker(channel, sticker_id)
            else:
                await bot.send_message(text=text, parse_mode='html', chat_id=channel)
        except TelegramBadRequest as e:
            continue
        except TelegramForbiddenError as e:
            continue
        except TelegramRetryAfter as e:
            sleep(e.retry_after)
            await bot.send_message(text=text, parse_mode='html', chat_id=channel)
    BD.delete_old()


#Ограничение доступа пользователям, которых нет в списке
@router.message(lambda message:str(message.from_user.id) not in config.ADMINS)
async def check_user_id(msg: Message):
    await msg.answer("Нет доступа")
    return

#Запуск бота и вход в режим бесконечного цикла
@router.message(Command("start"))
async def cmd_start(msg: Message):
    #Добавление кнопок
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='/add_admin', callback_data='add_admin'), types.KeyboardButton(text='/delete_admin', callback_data='delete_admin'))
    builder.row(types.KeyboardButton(text='/list_channels', callback_data='list_channels'), types.KeyboardButton(text='/restart', callback_data='restart'))
    builder.row(types.KeyboardButton(text='/post', callback_data='post'), types.KeyboardButton(text='/schedule', callback_data='schedule'))

    keyboard = builder.as_markup(resize_keyboard=True)
    await msg.answer("Бот запущен\nКоманды:\n/add_admin - Добавление админов в каналы\n/delete_admin - Удаление админов из каналов\n/list_channels - Информация о каналах\n/post - Отправка постов в каналы\n/schedule - Все запланированые сообщения\n/restart - Перезапуск всего бота\n", reply_markup=keyboard)


async def get_chat_subscribers(chat_id):
    chat = await bot.get_chat(chat_id)
    count = await bot.get_chat_member_count(chat_id)
    return f"{chat_id} {count}\n{chat.title}\n"


@router.message(Command("list_channels"))
async def get_subscribers(msg: Message):
    text = ""
    for chat_id in config.CHANELLS_ID:
        try:
            text += await get_chat_subscribers(chat_id)
            text += await PR.get_admins(chat_id)
            text += "\n"
            answer_len = len(text)
            if answer_len >= 3500 and config.CHANELLS_ID[-1] != chat_id:
                await msg.answer(text)
                text = ""
        except TelegramBadRequest as e:
            text += f"{chat_id} - не удалось получить, проверьте есть ли бот в канале\n"
            continue
        except TelegramForbiddenError as e:
            text += f"{chat_id} - не удалось получить, скорее всего бот был кикнут из канала\n"
            continue
        except TelegramRetryAfter as e:
            sleep(e.retry_after)
            text += await get_chat_subscribers(chat_id)
            text += await PR.get_admins(chat_id)
    await msg.answer(text)


#Перезапуск бота
@router.message(Command("restart"))
async def restart(msg: Message):
    await msg.answer("Перезапуск бота...\n")
    python = sys.executable
    os.execl(python, python, *sys.argv)

@router.message(Command("schedule"))
async def schedule(msg: Message):
    posts = BD.select_all()
    for post in posts:
        builder = InlineKeyboardBuilder()
        if post[3] != 'false':
            button = types.InlineKeyboardButton(text="Удалить" , callback_data=f"ID:{post[0]}")
            builder.add(button)
            keyboard = builder.as_markup(resize_keyboard=True)
            await msg.answer_photo(post[3], caption=f"Дата: {post[1]}\n{post[2]}", parse_mode='html', reply_markup=keyboard)
        elif post[4] != 'false':
            button = types.InlineKeyboardButton(text="Удалить" , callback_data=f"ID:{post[0]}")
            builder.add(button)
            keyboard = builder.as_markup(resize_keyboard=True)
            await msg.answer_sticker(post[4])
            await msg.answer(f"Дата: {post[1]}\n", parse_mode='html', reply_markup=keyboard)
        else:
            button = types.InlineKeyboardButton(text="Удалить" , callback_data=f"ID:{post[0]}")
            builder.add(button)
            keyboard = builder.as_markup(resize_keyboard=True)
            await msg.answer(f"Дата: {post[1]}\n{post[2]}", parse_mode='html', reply_markup=keyboard)

@router.callback_query(lambda c: "ID" in c.data)
async def delet_task(callback_query: types.CallbackQuery):
    id = callback_query.data.split(":")[1]
    job_id = BD.select_by_id(id)[0]
    SCHEDULER.remove_job(job_id)
    BD.delete_by_id(id)
    await callback_query.message.answer(f"Задача удалена")

#Цепочка post
@router.message(Command('post'))
async def cmd_post(message: types.Message, state: FSMContext):
    await state.set_state(SendMessage.post_text)
    await message.answer("Отправьте сообщение, которое нужно разослать")
    
@router.message(SendMessage.post_text, F.text)
async def process_message(message: types.Message, state: FSMContext):
    await state.update_data(post_text=message.text)
    await when_buttuns(message, state)

@router.message(SendMessage.post_text, F.sticker)
async def process_message(message: types.Message, state: FSMContext):
    await state.update_data(sticker_id=message.sticker.file_id)
    await when_buttuns(message, state)

@router.message(SendMessage.post_text, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(image_id=message.photo[0].file_id)
    await message.answer("Отправьте описание к фото")

async def when_buttuns(message: types.Message, state: FSMContext):  
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='Cейчас', callback_data='send_now'), types.InlineKeyboardButton(text='По расписанию', callback_data='schedule_send'))
    keyboard = builder.as_markup(resize_keyboard=True)
    await state.set_state(SendMessage.when)
    await message.answer("Выберите вариант отправки:", reply_markup=keyboard)

async def get_vaule(tag, text):
    if f'{tag}' in text.keys():
        tag = text[f'{tag}']
    else:
        tag = 'false'
    return tag

@router.callback_query(SendMessage.when, lambda c: c.data == 'send_now')
async def send_now(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(when=callback_query.data)
    text = await state.get_data()
    image_id = await get_vaule('image_id', text)
    sticker_id = await get_vaule('sticker_id', text)
    post_text = await get_vaule('post_text', text)
    await send_post(text=post_text, image_id=image_id, sticker_id=sticker_id)
    await state.clear()
    await callback_query.message.answer("Сообщение отправлено")

@router.callback_query(SendMessage.when, lambda c: c.data == 'schedule_send')
async def schedule_date(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(when=callback_query.data)
    await state.set_state(SendMessage.schedule_date)
    await callback_query.message.answer(
        "Выберете дату: ",
        reply_markup=await SimpleCalendar().start_calendar())

@router.callback_query(SendMessage.schedule_date, SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime.today() - timedelta(days=1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(schedule_date=date)
        builder = InlineKeyboardBuilder()
        for i in range(0, 24):
            button = types.InlineKeyboardButton(text=str(i) , callback_data=str(i))
            builder.add(button)
        keyboard = builder.as_markup(resize_keyboard=True)
        await callback_query.message.answer("Выберете время: ", reply_markup=keyboard)
        await state.set_state(SendMessage.schedule_time)

@router.callback_query(SendMessage.schedule_time)
async def schedule_time(callback_query: types.CallbackQuery, state: FSMContext):
    if int(callback_query.data) < datetime.now().hour:
        await callback_query.message.answer("Данное время уже прошло")
        return
    builder = InlineKeyboardBuilder()
    for i in range(0, 60):
        button = types.InlineKeyboardButton(text=str(i) , callback_data=str(i))
        builder.add(button)
    keyboard = builder.as_markup(resize_keyboard=True)
    await state.update_data(schedule_time=callback_query.data)
    await callback_query.message.answer(f"Выберете время", reply_markup=keyboard)
    await state.set_state(SendMessage.schedule_minute)


@router.callback_query(SendMessage.schedule_minute)
async def schedule_minute(callback_query: types.CallbackQuery, state: FSMContext):
    text = await state.get_data()
    time = datetime.strptime(f"{text['schedule_time']}:{callback_query.data}", '%H:%M')
    time_delta = timedelta(hours=time.hour, minutes=time.minute)
    
    selected_date = text['schedule_date'] + time_delta
    if selected_date < datetime.now():
        await callback_query.message.answer("Данное время уже прошло")
        return
    await state.update_data(schedule_time=callback_query.data)
    image_id = await get_vaule('image_id', text)
    sticker_id = await get_vaule('sticker_id', text)
    post_text = await get_vaule('post_text', text)
    await add_task(selected_date, post_text, image_id, sticker_id)
    await callback_query.message.answer(f"Сообщение запланировано на {selected_date}")
    await state.clear()

        
    
    
#обработка цепочки add_admin
@router.message(Command('add_admin'))
async def ask_id(message: types.Message, state: FSMContext):
    await state.set_state(AddAdmin.admins_id)
    await message.answer("Введите id админов которых нужно добавить")


@router.message(AddAdmin.admins_id)
async def get_admins_id(message: types.Message, state: FSMContext):
    get_id = message.text.replace(" ", "").split(',')
    await state.update_data(admins_id=get_id)
    for id in get_id:
        add_to = ""
        for chat_id in config.CHANELLS_ID:
            try:
                await bot.promote_chat_member(chat_id, id, 
                                            is_anonymous=config.IS_ANON, can_manage_chat=config.MANAGE_CHAT, can_delete_messages=config.DELETE_MESSAGE,
                                            can_manage_video_chats=config.MANAGE_VIDEO, can_restrict_members=config.RESTRICT_MEMBERS, can_promote_members=config.PROMOTE_MEMBERS,
                                            can_change_info=config.CHANGE_INFO, can_invite_users=config.INVITE_USERS, can_post_stories=config.POST_STORIES,
                                            can_edit_stories=config.EDIT_STORIES, can_delete_stories=config.DELETE_STORIES, can_post_messages=config.POST_MESSAGES,
                                            can_edit_messages=config.EDIT_MESSAGES, can_pin_messages=config.PIN_MESSAGES, can_manage_topics=config.MANAGE_TOPIC)
                add_to += f"{chat_id}, "
            except TelegramBadRequest as e:
                if 'CHAT_ADMIN_INVITE_REQUIRED' in e.message or 'user not found' in e.message:
                    await message.answer(f"Пользователя нет в канале:\nchat_id: {chat_id} admin_id: {id}")
                    continue
                await message.answer(f"Недостаточно прав:\nchat_id: {chat_id} admin_id: {id}")
                continue
            except TelegramForbiddenError as e:
                continue
        if add_to != "":
            await message.answer(f"Админ {id} добавлен в чаты: {add_to}")
        else:
            await message.answer(f"Не удалось добавить админа из чатов")
    await state.clear()

#обработка цепочки delete_admin
@router.message(Command('delete_admin'))
async def ask_id(message: types.Message, state: FSMContext):
    await state.set_state(DeleteAdmin.admins_id)
    await message.answer("Введите id админов которых нужно добавить")

@router.message(DeleteAdmin.admins_id)
async def get_admins_id(message: types.Message, state: FSMContext):
    get_id = message.text.replace(" ", "").split(',')
    await state.update_data(admins_id=get_id)
    for id in get_id:
        del_from = ""
        for chat_id in config.CHANELLS_ID:
            try:
                await bot.promote_chat_member(chat_id, id,
                                            is_anonymous=False, can_manage_chat=False, can_delete_messages=False,
                                            can_manage_video_chats=False, can_restrict_members=False, can_promote_members=False,
                                            can_change_info=False, can_invite_users=False, can_post_stories=False,
                                            can_edit_stories=False, can_delete_stories=False, can_post_messages=False,
                                            can_edit_messages=False, can_pin_messages=False, can_manage_topics=False)
                del_from += f"{chat_id}, "
            except TelegramBadRequest as e:
                if 'CHAT_ADMIN_INVITE_REQUIRED' in e.message or 'user not found' in e.message:
                    await message.answer(f"Пользователя нет в канале:\nchat_id: {chat_id} admin_id: {id}")
                    continue
                await message.answer(f"Недостаточно прав:\nchat_id: {chat_id} admin_id: {id}")
                continue
            except TelegramForbiddenError as e:
                continue
        if del_from != "":
            await message.answer(f"Админ {id} удален из чатов: {del_from}")
        else:
            await message.answer(f"Не удалось удалить админа из чатов")
    await state.clear()