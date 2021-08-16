from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from entity.enums.Race import Race
from entity.enums.SellMenuOption import SellMenuOption
from entity.enums.Server import Server


def get_sell_menu_kb(cb_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text='Выставить персонажа на продажу',
        callback_data=enc_cb_data(cb_key, SellMenuOption.new_lot.name))
    )
    kb.add(InlineKeyboardButton(
        text='Просмотреть ваши активные лоты',
        callback_data=enc_cb_data(cb_key, SellMenuOption.show_lots.name))
    )
    kb.add(InlineKeyboardButton(
        text='Удалить лот',
        callback_data=enc_cb_data(cb_key, SellMenuOption.remove_lot.name))
    )
    return kb


def get_race_select_kb(cb_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Люди', callback_data=enc_cb_data(cb_key, Race.human.name)))
    kb.add(InlineKeyboardButton(text='Зооморфы', callback_data=enc_cb_data(cb_key, Race.untamed.name)))
    kb.add(InlineKeyboardButton(text='Сиды', callback_data=enc_cb_data(cb_key, Race.winged_elf.name)))
    kb.add(InlineKeyboardButton(text='Древние', callback_data=enc_cb_data(cb_key, Race.earthguard.name)))
    kb.add(InlineKeyboardButton(text='Тени', callback_data=enc_cb_data(cb_key, Race.nightshade.name)))
    kb.add(InlineKeyboardButton(text='Амфибии', callback_data=enc_cb_data(cb_key, Race.tideborn.name)))
    return kb


def get_server_selector_kb(cb_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Арктур', callback_data=enc_cb_data(cb_key, Server.arcturus.name)))
    kb.add(InlineKeyboardButton(text='Скорпион', callback_data=enc_cb_data(cb_key, Server.scorpion.name)))
    kb.add(InlineKeyboardButton(text='Саргас', callback_data=enc_cb_data(cb_key, Server.sargaz.name)))
    kb.add(InlineKeyboardButton(text='Гиперион', callback_data=enc_cb_data(cb_key, Server.hyperion.name)))
    return kb


def enc_cb_data(key: str, value: str) -> str:
    assert len(key.split('__')) == 1 and len(value.split('__')) == 1
    return f'{key}__{value}'


def dec_cb_data(token: str) -> (str, str):
    return token.split('__')[0], token.split('__')[1]
