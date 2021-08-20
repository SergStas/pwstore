from telebot.types import Message, CallbackQuery
from bot.spell.SpellHandler import SpellHandler
from bot.utils.bot_utils import init_bot, check_user_session
from bot.validation.input_validation import validate_class, validate_lvl, validate_heaven, validate_description, \
    validate_doll, validate_price, validate_contacts
from bot.utils.ui_constr import get_race_select_kb, dec_cb_data, get_server_selector_kb, get_sell_menu_kb, \
    get_search_results_kb, get_remove_button, get_remove_confirm_kb
from entity.dataclass.LotData import LotData
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
        'new_lot_race': __new_lot_race_cb,
        'search_lot': __search_lot_cb,
        'user_lots': __user_lots_cb,
        'close': __close_lot_cb,
        'close_conf': __close_conf_cb
    }
    key_dict[key](call, value)


def __close_lot_cb(call: CallbackQuery, value):
    lot_id = int(value.split('_')[1])
    __bot.delete_message(call.from_user.id, call.message.id)
    __bot.send_message(
        call.from_user.id,
        SpellHandler.get_message(Event.close_lot_confirm),
        reply_markup=get_remove_confirm_kb('close_conf', lot_id)
    )


def __close_conf_cb(call: CallbackQuery, value):
    lot_id = int(value.split('_')[1])
    option = value.split('_')[0]
    __bot.delete_message(call.from_user.id, call.message.id)
    if option == 'yes':
        DBController.close_lot(lot_id)
        __send(call.from_user.id, Event.close_lot_success)


def __search_lot_cb(call: CallbackQuery, value, user_lots: bool = False):
    if 'page_' in value:
        __bot.delete_message(call.from_user.id, call.message.id)
        page = int(value.split('_')[1])
        if user_lots:
            lots = DBController.get_user_lots(call.from_user.id)
            __send_page_message(page, lots, call.from_user.id, 'search_lot')
        else:
            __proceed_lots_request(call.from_user.id, page)
        return
    lot_id = int(value)
    lot = DBController.get_lot(lot_id)
    text = SpellHandler.get_message(
        Event.lot_info_template,
        (
            lot.char.server,
            lot.char.race,
            lot.char.lvl,
            lot.char.char_class,
            lot.char.heavens,
            lot.char.doll,
            lot.price,
            lot.user.username,
            lot.contact_info,
            lot.date_opened,
            lot.char.description
        ))
    reply_markup = None if not user_lots else get_remove_button(f'close', lot.lot_id)
    __bot.send_message(call.from_user.id, text, reply_markup=reply_markup)


def __sell_menu_cb(call: CallbackQuery, value: str):
    __bot.delete_message(call.from_user.id, call.message.id)
    option = SellMenuOption[value]
    if option == SellMenuOption.new_lot:
        __bot.send_message(
            chat_id=call.from_user.id,
            text=SpellHandler.get_message(Event.new_lot_input_server),
            reply_markup=get_server_selector_kb('new_lot_server')
        )
    elif option == SellMenuOption.show_lots:
        user_lots = DBController.get_user_lots(call.from_user.id)
        if len(user_lots) == 0:
            __send(call.from_user.id, Event.no_user_lots_found)
        else:
            __send_page_message(0, user_lots, call.from_user.id, 'user_lots')


def __user_lots_cb(call: CallbackQuery, value: str):
    __search_lot_cb(call, value, user_lots=True)


def __new_lot_server_cb(call: CallbackQuery, value: str):
    __default_cb_handle(
        call=call,
        value=value,
        commit_func=lambda user_id, val:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.server, Server[val]),
        spell_event=Event.new_lot_input_race,
        reply_markup=get_race_select_kb('new_lot_race')
    )


def __new_lot_race_cb(call: CallbackQuery, value: str):
    __bot.delete_message(call.from_user.id, call.message.id)
    DBController.update_new_lot_session_params(call.from_user.id, NewLotSessionParam.race, Race[value])
    __send(call.from_user.id, Event.new_lot_input_class)
    __bot.register_next_step_handler(call.message, __new_lot_class_step)


def __new_lot_class_step(message: Message):
    __default_input_validation_step(
        message=message,
        validation_func=validate_class,
        commit_func=lambda user_id, value:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.char_class, value),
        error_msg_arg='класса персонажа',
        next_step=Event.new_lot_input_lvl,
        next_step_handler=__new_lot_lvl_step,
        handler_self_ref=__new_lot_class_step
    )


def __new_lot_lvl_step(message: Message):
    __default_input_validation_step(
        message=message,
        validation_func=validate_lvl,
        commit_func=lambda user_id, value:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.lvl, int(value)),
        error_msg_arg='уровня персонажа',
        next_step=Event.new_lot_input_heaven,
        next_step_handler=__new_lot_heaven_step,
        handler_self_ref=__new_lot_lvl_step
    )


def __new_lot_heaven_step(message: Message):
    __default_input_validation_step(
        message=message,
        validation_func=validate_heaven,
        commit_func=lambda user_id, value:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.heavens, value),
        error_msg_arg='уровня неба персонажа',
        next_step=Event.new_lot_input_doll,
        next_step_handler=__new_lot_doll_step,
        handler_self_ref=__new_lot_heaven_step
    )


def __new_lot_doll_step(message: Message):
    __default_input_validation_step(
        message=message,
        validation_func=validate_doll,
        commit_func=lambda user_id, value:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.doll, value),
        error_msg_arg='куклы персонажа',
        next_step=Event.new_lot_input_description,
        next_step_handler=__new_lot_description_step,
        handler_self_ref=__new_lot_doll_step
    )


def __new_lot_description_step(message: Message):
    __default_input_validation_step(
        message=message,
        validation_func=validate_description,
        commit_func=lambda user_id, value:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.description, value),
        error_msg_arg='описания персонажа',
        next_step=Event.new_lot_input_price,
        next_step_handler=__new_lot_price_step,
        handler_self_ref=__new_lot_description_step
    )


def __new_lot_price_step(message: Message):
    __default_input_validation_step(
        message=message,
        validation_func=validate_price,
        commit_func=lambda user_id, value:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.price, float(value)),
        error_msg_arg='цены на персонажа',
        next_step=Event.new_lot_input_contacts,
        next_step_handler=__new_lot_contacts_step,
        handler_self_ref=__new_lot_price_step
    )


def __new_lot_contacts_step(message: Message):
    if not validate_contacts(message.text.strip()):
        __send(message.from_user.id, Event.invalid_value, (message.text.strip(), 'контактов',))
        __bot.register_next_step_handler(message, __new_lot_contacts_step)
        return
    DBController.update_new_lot_session_params(
        message.from_user.id,
        NewLotSessionParam.contact_info,
        message.text.strip()
    )
    add_result = DBController.create_lot(message.from_user.id)
    __send(
        message.from_user.id,
        Event.new_lot_success if add_result else Event.new_lot_fail
    )


def __search_race_cb(call: CallbackQuery, value: str):
    __bot.delete_message(call.from_user.id, call.message.id)
    DBController.update_search_session_params(call.from_user.id, SearchSessionParam.race, Race[value])
    __proceed_lots_request(call.from_user.id)


def __proceed_lots_request(user_id: int, page: int = 0):
    lots, event = DBController.get_filtered_lots(user_id)
    if event == Event.no_lots_found or event == Event.db_error:
        __send(user_id, event)
        return
    __send(user_id, Event.filtered_lots_found, (len(lots),))
    __send_page_message(page, lots, user_id, 'search_race')


def __send_page_message(page: int, lots: [LotData], user_id: int, key: str, size=10):
    start = page * size
    end = min(len(lots), (page + 1) * size) - 1
    __bot.send_message(
        chat_id=user_id,
        text=SpellHandler.get_message(Event.show_lots_indices, (start, end, page,)),
        reply_markup=get_search_results_kb(lots, page, key, size)
    )


def __search_server_cb(call: CallbackQuery, value: str):
    __default_cb_handle(
        call=call,
        value=value,
        commit_func=lambda user_id, val:
            DBController.update_search_session_params(user_id, SearchSessionParam.server, Server[val]),
        spell_event=Event.search_select_race,
        reply_markup=get_race_select_kb('search_race')
    )


def __send(user_id: int, event: Event, args=None) -> None:
    __bot.send_message(user_id, SpellHandler.get_message(event, args))


def __check_mes(message: Message, show_greeting=False):
    user = UserData(message.from_user.id, message.from_user.username, message.from_user.full_name)
    if not check_user_session(user):
        if show_greeting:
            handle_greeting(message)
    Logger.debug(f'User {message.from_user.id} has sent message: {message.text}')


def start_bot():
    Logger.debug('Bot polling has started')
    __bot.polling(none_stop=True)


def __default_cb_handle(
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


def __default_input_validation_step(
        message: Message,
        validation_func,
        commit_func,
        error_msg_arg: str,
        next_step: Event,
        next_step_handler,
        handler_self_ref
):
    if not validation_func(message.text.strip()):
        __send(message.from_user.id, Event.invalid_value, (message.text.strip(), error_msg_arg,))
        __bot.register_next_step_handler(message, handler_self_ref)
        return
    commit_func(message.from_user.id, message.text.strip())
    __send(message.from_user.id, next_step)
    __bot.register_next_step_handler(message, next_step_handler)
