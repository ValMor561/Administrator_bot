import config  
from pyrogram import Client
from pyrogram import enums

class PyroGRAMM:
    def __init__(self):
        self.app = Client("Имя | Бот", api_id=config.CLIENT_ID, api_hash=config.CLIENT_HASH, bot_token=config.BOT_TOKEN, in_memory=True)
        self.app.start()

    def __del__(self):
        self.app.stop()


    async def get_chat_members(self, chat_id):
        chat_members = []
        async for member in self.app.get_chat_members(int(chat_id)):
            chat_members = chat_members + [member.user.id]
        return chat_members

    async def get_admins(self, chat_id):
        administrators = "Администраторы: \n"
        async for m in self.app.get_chat_members(int(chat_id), filter=enums.ChatMembersFilter.ADMINISTRATORS):
            administrators += f"{m.user.id} : {m.user.username}\n"
        return administrators

    async def get_bots(self, chat_id):
        administrators = "Список ботов: \n"
        async for m in self.app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.BOTS):
            administrators += f"{m.user.id} : {m.user.username}\n"
        return administrators
