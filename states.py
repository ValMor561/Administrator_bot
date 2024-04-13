from aiogram.filters.state import State, StatesGroup

class SendMessage(StatesGroup):
    post_text = State()
    image_id = State()
    sticker_id = State()
    when = State()
    schedule = State()

class AddAdmin(StatesGroup):
    admins_id = State()

class DeleteAdmin(StatesGroup):
    admins_id = State()