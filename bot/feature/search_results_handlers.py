from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.cb_utils import send_default_page, send, lots_list_default_handler
from controllers.DBController import DBController
from entity.enums.Event import Event


def all_lots_cb(call: CallbackQuery, value, bot: TeleBot):
    lots_list_default_handler(
        bot=bot,
        call=call,
        value=value,
        page_switcher=__proceed_lots_request,
        markup_factory=None
    )


def __proceed_lots_request(bot: TeleBot, call: CallbackQuery, page: int):
    lots, event = DBController.get_filtered_lots(call.from_user.id)
    if event == Event.no_lots_found or event == Event.db_error:
        send(bot, call.from_user.id, event)
        return
    send_default_page(bot, page, lots, call.from_user.id, 'show_lots')
