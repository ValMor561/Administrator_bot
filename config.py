import configparser
from distutils.util import strtobool
from datetime import datetime, timezone


#Чтение конфигурационного файла
def get_config(filename):
    config = configparser.ConfigParser()
    config.read(filename, encoding="utf-8")

    return config

#Функция для считывания значений из файла если он указан в качестве параметра, либо из .ini файла
#На вход подается значение хранящееся в конфиге
def get_multiple_values(param):
    if ".txt" in param:
        with open(param, encoding = 'utf-8', mode = 'r') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    return param.replace(" ", "").split(',')

config = get_config('config.ini')

#Глобальные переменные всех параметров
BOT_TOKEN = config['DEFAULT']['bot_token']
CHANELLS_ID = get_multiple_values(config['DEFAULT']['channels_id'])
ADMINS = get_multiple_values(config['DEFAULT']['admins'])
CLIENT_ID = config['pyrogram']['client_id']
CLIENT_HASH = config['pyrogram']['client_hash']
HOST=config['BD']['host']
DATABASE=config['BD']['database']
USER=config['BD']['user']
PASSWORD=config['BD']['password']
TABLENAME=config['BD']['tablename']
IS_ANON = strtobool(config['PRIVILEGES']['is_anonymous'])
MANAGE_CHAT= strtobool(config['PRIVILEGES']['can_manage_chat'])
DELETE_MESSAGE = strtobool(config['PRIVILEGES']['can_delete_messages'])
MANAGE_VIDEO = strtobool(config['PRIVILEGES']['can_manage_video_chats'])
RESTRICT_MEMBERS = strtobool(config['PRIVILEGES']['can_restrict_members'])
PROMOTE_MEMBERS = strtobool(config['PRIVILEGES']['can_promote_members'])
CHANGE_INFO = strtobool(config['PRIVILEGES']['can_change_info'])
INVITE_USERS = strtobool(config['PRIVILEGES']['can_invite_users'])
POST_STORIES = strtobool(config['PRIVILEGES']['can_post_stories'])
EDIT_STORIES = strtobool(config['PRIVILEGES']['can_edit_stories'])
DELETE_STORIES = strtobool(config['PRIVILEGES']['can_delete_stories'])
POST_MESSAGES = strtobool(config['PRIVILEGES']['can_post_messages'])
EDIT_MESSAGES = strtobool(config['PRIVILEGES']['can_edit_messages'])
PIN_MESSAGES = strtobool(config['PRIVILEGES']['can_pin_messages'])
MANAGE_TOPIC = strtobool(config['PRIVILEGES']['can_manage_topics'])
UNPIN_TIME =  datetime.strptime(config['SETTINGS']['unpin_time'], '%Y.%m.%d %H:%M').astimezone(timezone.utc)
UNPIN_TEXT = get_multiple_values(config['SETTINGS']['unpin_text'])