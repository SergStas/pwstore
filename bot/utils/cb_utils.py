from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from bot.spell.SpellHandler import SpellHandler
from bot.utils.ui_constr import get_search_results_kb
from controllers.DBController import DBController
from entity.dataclass.LotData import LotData
from entity.enums.Event import Event


def default_cb_handler(
        bot,
        call: CallbackQuery,
        value,
        commit_func,
        spell_event: Event,
        reply_markup,
        spell_args=None
):
    bot.delete_message(call.from_user.id, call.message.id)
    commit_func(call.from_user.id, value)
    bot.send_message(
        chat_id=call.from_user.id,
        text=SpellHandler.get_message(spell_event) if spell_args is None else SpellHandler.get_message(
            spell_event, *spell_args
        ),
        reply_markup=reply_markup
    )


def default_input_validation_step(
        bot,
        message: Message,
        validation_func,
        commit_func,
        error_msg_arg: str,
        next_step: Event,
        next_step_handler,
        handler_self_ref
):
    if not validation_func(message.text.strip()):
        send(bot, message.from_user.id, Event.invalid_value, (message.text.strip(), error_msg_arg,))
        bot.register_next_step_handler(message, handler_self_ref)
        return
    commit_func(message.from_user.id, message.text.strip())
    send(bot, message.from_user.id, next_step)
    bot.register_next_step_handler(message, next_step_handler)


def lots_list_default_handler(bot: TeleBot, call: CallbackQuery, value, page_switcher, markup_factory):
    if 'page_' in value:
        bot.delete_message(call.from_user.id, call.message.id)
        page = int(value.split('_')[1])
        page_switcher(bot, call, page)
        return
    lot = DBController.get_lot(int(value))
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
    bot.send_message(call.from_user.id, text, reply_markup=markup_factory(lot))


def send_default_page(bot: TeleBot, page: int, lots: [LotData], user_id: int, key: str, size=5):
    start = page * size
    end = min(len(lots), (page + 1) * size) - 1
    bot.send_message(
        chat_id=user_id,
        text=SpellHandler.get_message(Event.show_lots_indices, (start, end, page,)),
        reply_markup=get_search_results_kb(lots, page, key, size)
    )


def send(bot, user_id: int, event: Event, args=None) -> None:
    bot.send_message(user_id, SpellHandler.get_message(event, args))
