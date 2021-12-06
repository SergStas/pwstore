from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.cb_utils import send_default_page, send, lots_list_default_handler
from bot.utils.markup_factories import get_lots_list_default_markup_factory
from bot.utils.ui_constr import get_return_kb, get_all_lots_markup_kb
from controllers.DBController import DBController
from entity.enums.Event import Event


def all_lots_cb(call: CallbackQuery, value, bot: TeleBot, cb_key: str = 'show_lots'):
    lots_list_default_handler(
        bot=bot,
        call=call,
        value=value,
        page_switcher=__proceed_lots_request,
        markup_factory=get_lots_list_default_markup_factory(cb_key, call, with_seller_lots=True)
    )


def __proceed_lots_request(bot: TeleBot, call: CallbackQuery, page: int):
    lots, event = DBController.get_filtered_lots(call.from_user.id)
    if event == Event.no_lots_found or event == Event.db_error:
        send(bot, call.from_user.id, event, None, get_return_kb())
        return
    send_default_page(bot, page, lots, call.from_user.id, 'show_lots')
