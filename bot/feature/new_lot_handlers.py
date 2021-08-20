from typing import Optional

from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from bot.utils.cb_utils import default_cb_handler, send, default_input_validation_step
from bot.utils.ui_constr import get_race_select_kb
from bot.validation.input_validation import validate_class, validate_lvl, validate_heaven, validate_doll, \
    validate_description, validate_price, validate_contacts
from controllers.DBController import DBController
from entity.enums.Event import Event
from entity.enums.NewLotSessionParam import NewLotSessionParam
from entity.enums.Race import Race
from entity.enums.Server import Server


__bot: Optional[TeleBot] = None


def new_lot_server_cb(call: CallbackQuery, value: str, bot: TeleBot):
    __set_bot(bot)
    default_cb_handler(
        bot,
        call=call,
        value=value,
        commit_func=lambda user_id, val:
            DBController.update_new_lot_session_params(user_id, NewLotSessionParam.server, Server[val]),
        spell_event=Event.new_lot_input_race,
        reply_markup=get_race_select_kb('new_lot_race')
    )


def new_lot_race_cb(call: CallbackQuery, value: str, bot: TeleBot):
    __set_bot(bot)
    bot.delete_message(call.from_user.id, call.message.id)
    DBController.update_new_lot_session_params(call.from_user.id, NewLotSessionParam.race, Race[value])
    send(bot, call.from_user.id, Event.new_lot_input_class)
    bot.register_next_step_handler(call.message, __new_lot_class_step)


def __new_lot_class_step(message: Message):
    default_input_validation_step(
        __bot,
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
    default_input_validation_step(
        __bot,
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
    default_input_validation_step(
        __bot,
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
    default_input_validation_step(
        __bot,
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
    default_input_validation_step(
        __bot,
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
    default_input_validation_step(
        __bot,
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
        send(__bot, message.from_user.id, Event.invalid_value, (message.text.strip(), 'контактов',))
        __bot.register_next_step_handler(message, __new_lot_contacts_step)
        return
    DBController.update_new_lot_session_params(
        message.from_user.id,
        NewLotSessionParam.contact_info,
        message.text.strip()
    )
    add_result = DBController.create_lot(message.from_user.id)
    send(
        __bot,
        message.from_user.id,
        Event.new_lot_success if add_result else Event.new_lot_fail
    )


def __set_bot(bot: TeleBot):
    global __bot
    __bot = bot
