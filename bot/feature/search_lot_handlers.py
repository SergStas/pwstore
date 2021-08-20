from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.feature.search_results_handlers import all_lots_cb
from bot.utils.cb_utils import default_cb_handler
from bot.utils.ui_constr import get_race_select_kb
from controllers.DBController import DBController
from entity.enums.Event import Event
from entity.enums.Race import Race
from entity.enums.SearchSessionParam import SearchSessionParam
from entity.enums.Server import Server


def search_server_cb(call: CallbackQuery, value: str, bot: TeleBot):
    default_cb_handler(
        bot=bot,
        call=call,
        value=value,
        commit_func=lambda user_id, val:
            DBController.update_search_session_params(user_id, SearchSessionParam.server, Server[val]),
        spell_event=Event.search_select_race,
        reply_markup=get_race_select_kb('search_race')
    )


def search_race_cb(call: CallbackQuery, value: str, bot: TeleBot):
    DBController.update_search_session_params(call.from_user.id, SearchSessionParam.race, Race[value])
    all_lots_cb(call, 'page_0', bot)
