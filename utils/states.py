from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_phone = State()


class Checkout(StatesGroup):
    name = State()
    city = State()
    address = State()
    comment = State()
    confirm = State()


class Support(StatesGroup):
    waiting_message = State()


class SupportReply(StatesGroup):
    waiting_reply = State()


class AddProduct(StatesGroup):
    category = State()
    new_category_ru = State()
    new_category_uz = State()
    name_ru = State()
    name_uz = State()
    short_ru = State()
    short_uz = State()
    full_ru = State()
    full_uz = State()
    price = State()
    old_price = State()
    photo_main = State()
    photo_extra = State()
    characteristics = State()
    confirm = State()


class EditProduct(StatesGroup):
    choose_category = State()
    choose_product = State()
    choose_field = State()
    waiting_value = State()


class SetDeliveryPrice(StatesGroup):
    waiting_price = State()


class Broadcast(StatesGroup):
    choose_type = State()
    waiting_content = State()
    confirm = State()


class SettingEdit(StatesGroup):
    waiting_value = State()


class OrderSearch(StatesGroup):
    waiting_query = State()
