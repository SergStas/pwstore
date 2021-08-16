from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.SpellHandler import SpellHandler
from bot.bot_utils import init_bot, check_user_session
from bot.ui_constr import get_race_select_kb, dec_cb_data, get_server_selector_kb, get_sell_menu_kb
from entity.dataclass.UserData import UserData
from entity.enums.NewLotSessionParam import NewLotSessionParam
from entity.enums.Race import Race
from entity.enums.SearchSessionParam import SearchSessionParam
from entity.enums.SellMenuOption import SellMenuOption
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
    __bot.send_message(
        chat_id=message.from_user.id,
        text=SpellHandler.get_message(Event.sell_menu),
        reply_markup=get_sell_menu_kb('sell_menu')
    )


@__bot.message_handler(commands=['buy'])
def handle_buy_menu(message: Message):
    __check_mes(message)
    __bot.send_message(
        chat_id=message.from_user.id,
        text=SpellHandler.get_message(Event.search_select_server),
        reply_markup=get_server_selector_kb('search_server')
    )


@__bot.message_handler(content_types=['text'])
def handle_other(message: Message):
    __check_mes(message, True)
    __send(message.from_user.id, Event.unknown_command, (message.text,))


@__bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    key, value = dec_cb_data(call.data)
    key_dict = {
        'search_server': __search_server_cb,
        'search_race': __search_race_cb,
        'sell_menu': __sell_menu_cb,
        'new_lot_server': __new_lot_server_cb,
        'new_lot_race': __new_lot_race_cb
    }
    key_dict[key](call, value)


def __sell_menu_cb(call: CallbackQuery, value: str):
    __bot.delete_message(call.from_user.id, call.message.id)
    option = SellMenuOption[value]
    if option == SellMenuOption.new_lot:
        __bot.send_message(
            chat_id=call.from_user.id,
            text=SpellHandler.get_message(Event.sell_input_server),
            reply_markup=get_server_selector_kb('new_lot_server')
        )
    else:
        pass  # TODO


def __new_lot_server_cb(call: CallbackQuery, value: str):
    __apply_param_default_cb(
        call=call,
        value=value,
        commit_func=lambda user_id, val:
            DBController.update_sell_session_params(user_id, NewLotSessionParam.server, Server[val]),
        spell_event=Event.sell_input_race,
        reply_markup=get_race_select_kb('new_lot_race')
    )
    # __bot.delete_message(call.from_user.id, call.message.id)
    # DBController.update_sell_session_params(call.from_user.id, NewLotSessionParam.server, Server[value])
    # __bot.send_message(
    #     chat_id=call.from_user.id,
    #     text=SpellHandler.get_message(Event.sell_input_race),
    #     reply_markup=get_race_select_kb('new_lot_race')
    # )


def __new_lot_race_cb(call: CallbackQuery, value: str):
    pass  # TODO


def __search_race_cb(call: CallbackQuery, value: str):
    __bot.delete_message(call.from_user.id, call.message.id)
    DBController.update_search_session_params(call.from_user.id, SearchSessionParam.race, Race[value])
    lots, event = DBController.get_filtered_lots(call.from_user.id)
    if event == Event.no_lots_found or event == Event.db_error:
        __send(call.from_user.id, event)
        return
    __bot.send_message(
        chat_id=call.from_user.id,
        text=SpellHandler.get_message(Event.filtered_lots_found, (len(lots),)),
        reply_markup=None
    )
    # TODO: show lots


def __search_server_cb(call: CallbackQuery, value: str):
    __apply_param_default_cb(
        call=call,
        value=value,
        commit_func=lambda user_id, val:
            DBController.update_search_session_params(user_id, SearchSessionParam.server, Server[val]),
        spell_event=Event.search_select_race,
        reply_markup=get_race_select_kb('search_race')
    )
    # __bot.delete_message(call.from_user.id, call.message.id)
    # DBController.update_search_session_params(call.from_user.id, SearchSessionParam.server, Server[value])
    # __bot.send_message(
    #     chat_id=call.from_user.id,
    #     text=SpellHandler.get_message(Event.search_select_race),
    #     reply_markup=get_race_select_kb('search_race')
    # )


def __send(user_id: int, event: Event, args=None) -> None:
    __bot.send_message(user_id, SpellHandler.get_message(event, args))


def __check_mes(message: Message, show_greeting=False):
    if not check_user_session(UserData(message.from_user.id)):
        if show_greeting:
            handle_greeting(message)
    Logger.debug(f'User {message.from_user.id} has sent message: {message.text}')


def start_bot():
    Logger.debug('Bot polling has started')
    __bot.polling(none_stop=True)


def __apply_param_default_cb(
        call: CallbackQuery,
        value,
        commit_func,
        spell_event: Event,
        reply_markup,
        spell_args=None
):
    __bot.delete_message(call.from_user.id, call.message.id)
    commit_func(call.from_user.id, value)
    __bot.send_message(
        chat_id=call.from_user.id,
        text=SpellHandler.get_message(spell_event) if spell_args is None else SpellHandler.get_message(
            spell_event, *spell_args
        ),
        reply_markup=reply_markup
    )
