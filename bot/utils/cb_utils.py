from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from bot.spell.SpellHandler import SpellHandler
from bot.utils.ui_constr import get_search_results_kb, get_return_kb
from controllers.DBController import DBController
from entity.dataclass.LotData import LotData
from entity.enums.Event import Event
from logger.Logger import Logger


def default_cb_handler(
        bot,
        call: CallbackQuery,
        value,
        commit_func,
        spell_event: Event,
        reply_markup,
        spell_args=None
):
    commit_func(call.from_user.id, value)
    send(
        bot,
        call.from_user.id,
        spell_event,
        spell_args,
        reply_markup
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
        send(bot, message.from_user.id, Event.invalid_value, (message.text.strip(), error_msg_arg,), get_return_kb())
        bot.register_next_step_handler(message, handler_self_ref)
        return
    commit_func(message.from_user.id, message.text.strip())
    send(
        bot,
        message.from_user.id,
        next_step,
        None,
        get_return_kb()
    )
    bot.register_next_step_handler(message, next_step_handler)


def lots_list_default_handler(bot: TeleBot, call: CallbackQuery, value, page_switcher, markup_factory):
    if 'page_' in value:
        page = int(value.split('_')[1])
        page_switcher(bot, call, page)
        return
    lot = DBController.get_lot(int(value))
    args = (
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
    )
    markup = markup_factory(lot) if markup_factory is not None else None
    send(
        bot,
        call.from_user.id,
        Event.lot_info_template,
        args,
        markup
    )


def send_default_page(bot: TeleBot, page: int, lots: [LotData], user_id: int, key: str, size=5):
    start = page * size
    end = min(len(lots), (page + 1) * size) - 1
    send(
        bot,
        user_id,
        Event.filtered_lots_found,
        (len(lots), start, end, page,),
        get_search_results_kb(lots, page, key, size)
    )


def send(bot: TeleBot, user_id: int, event: Event, args=None, markup=None) -> None:
    message = bot.send_message(user_id, SpellHandler.get_message(event, args), reply_markup=markup)
    cleanup_chat(bot, message.chat.id)
    DBController.save_message(message.id, message.chat.id)


def cleanup_chat(bot: TeleBot, chat_id: int) -> bool:
    ids = DBController.get_messages_to_delete(chat_id)
    result = True
    for message_id in ids:
        try:
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            Logger.error(f'Failed to delete message #{message_id} from chat #{chat_id}:\n\t\t\t{e}')
            result = False
        DBController.mark_message_as_deleted(message_id, chat_id)
    return result
