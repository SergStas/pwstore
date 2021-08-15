from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.SpellHandler import SpellHandler
from bot.bot_utils import init_bot, check_user_session
from entity.enums.Race import Race
from entity.enums.Server import Server
from entity.enums.Event import Event
from logger.LogLevel import LogLevel
from logger.Logger import Logger
from controllers.DBController import DBController

Logger.set_console_log_level(LogLevel.debug)
__bot = init_bot()


@__bot.message_handler(commands=['start'])
def handle_greeting(message: Message):
    __check_mes(message)
    __send(message.from_user.id, Event.first_launch)


@__bot.message_handler(commands=['help'])
def show_help(message: Message):
    __check_mes(message)
    __send(message.from_user.id, Event.help)


@__bot.message_handler(commands=['sell'])
def handle_sell_menu(message: Message):
    __check_mes(message)
    __bot.send_message(message.from_user.id, 'select server')  # TODO


@__bot.message_handler(commands=['buy'])
def handle_buy_menu(message: Message):
    __check_mes(message)
    __bot.send_message(
        chat_id=message.from_user.id,
        text=SpellHandler.get_message(Event.select_server),
        reply_markup=__get_server_selector_kb()
    )


@__bot.message_handler(content_types=['text'])
def handle_other(message: Message):
    __check_mes(message, True)
    __send(message.from_user.id, Event.unknown_command, (message.text,))


@__bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    key, value = __dec_cb_data(call.data)
    key_dict = {
        'server': __handle_server_callback,
        'race': __handle_race_callback
    }
    key_dict[key](call, value)


def __handle_race_callback(call: CallbackQuery, value: str):
    __bot.delete_message(call.from_user.id, call.message.id)
    DBController.update_search_session_params(call.from_user.id, race=Race[value])
    lots, event = DBController.get_filtered_lots(call.from_user.id)
    if event == Event.no_lots_found or event == Event.db_error:
        __send(call.from_user.id, event)
        return
    __bot.send_message(
        chat_id=call.from_user.id,
        text=SpellHandler.get_message(Event.filtered_lots_found, (len(lots),)),
        reply_markup=None
    )


def __handle_server_callback(call: CallbackQuery, value: str):
    __bot.delete_message(call.from_user.id, call.message.id)
    DBController.update_search_session_params(call.from_user.id, server=Server[value])
    __bot.send_message(
        chat_id=call.from_user.id,
        text=SpellHandler.get_message(Event.select_race),
        reply_markup=__get_race_select_kb()
    )
    # TODO: show lots


def __get_race_select_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Люди', callback_data=__enc_cb_data('race', Race.human.name)))
    kb.add(InlineKeyboardButton(text='Зооморфы', callback_data=__enc_cb_data('race', Race.untamed.name)))
    kb.add(InlineKeyboardButton(text='Сиды', callback_data=__enc_cb_data('race', Race.winged_elf.name)))
    kb.add(InlineKeyboardButton(text='Древние', callback_data=__enc_cb_data('race', Race.earthguard.name)))
    kb.add(InlineKeyboardButton(text='Тени', callback_data=__enc_cb_data('race', Race.nightshade.name)))
    kb.add(InlineKeyboardButton(text='Амфибии', callback_data=__enc_cb_data('race', Race.tideborn.name)))
    return kb


def __get_server_selector_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Арктур', callback_data=__enc_cb_data('server', Server.arcturus.name)))
    kb.add(InlineKeyboardButton(text='Скорпион', callback_data=__enc_cb_data('server', Server.scorpion.name)))
    kb.add(InlineKeyboardButton(text='Саргас', callback_data=__enc_cb_data('server', Server.sargaz.name)))
    kb.add(InlineKeyboardButton(text='Гиперион', callback_data=__enc_cb_data('server', Server.hyperion.name)))
    return kb


def __send(user_id: int, event: Event, args=None) -> None:
    __bot.send_message(user_id, SpellHandler.get_message(event, args))


def __check_mes(message: Message, show_greeting=False):
    if not check_user_session(message.from_user.id):
        if show_greeting:
            handle_greeting(message)
    Logger.debug(f'User {message.from_user.id} has sent message: {message.text}')


def __enc_cb_data(key: str, value: str) -> str:
    return f'{key}__{value}'


def __dec_cb_data(token: str) -> (str, str):
    return token.split('__')[0], token.split('__')[1]


def start_bot():
    Logger.debug('Bot polling has started')
    __bot.polling(none_stop=True)
