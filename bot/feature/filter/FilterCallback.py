from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.feature.filter.FilterKey import FilterKey
from controllers.DBController import DBController
from bot.feature.filter.FilterMarkupFactory import FilterMarkupFactory
from bot.feature.search_results_handlers import all_lots_cb
from bot.utils.cb_utils import send
from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder
from entity.enums.Event import Event
from entity.enums.SearchSessionParam import SearchSessionParam


class FilterCallback:
    @staticmethod
    def execute(call: CallbackQuery, value: str, bot: TeleBot):
        main_key = value.split('_')[0]
        if main_key == FilterKey.open.name:
            FilterCallback.__show_menu(call.from_user.id, bot)
        elif main_key == FilterKey.edit.name:
            FilterCallback.__edit_filter_param(call.from_user.id, value.split('_', 1)[1], bot)
        elif main_key == FilterKey.apply.name:
            FilterCallback.__apply_param(call.from_user.id, value.split('_', 1)[1], bot)
        elif main_key == FilterKey.close.name:
            FilterCallback.__close(call, bot)

    @staticmethod
    def __show_menu(user_id: int, bot: TeleBot):
        filter_params = DBController.get_filter_params(user_id)
        send(
            bot=bot,
            user_id=user_id,
            event=Event.filter_menu,
            markup=FilterMarkupFactory.get_filter_menu_markup(filter_params)
        )

    @staticmethod
    def __edit_filter_param(user_id: int, value: str, bot: TeleBot):
        event = FilterCallback.__extract_criteria(value)
        to_cb_data = lambda v, m: \
            CallbackKeyEncoder.enc_cb_data(FilterKey.filter.name, f'{FilterKey.apply.name}_{v.name}_{m.name}')
        if event == Event.input_min_lvl:
            cb_data = to_cb_data(FilterKey.lvl, FilterKey.min)
        elif event == Event.input_max_lvl:
            cb_data = to_cb_data(FilterKey.lvl, FilterKey.max)
        elif event == Event.input_min_price:
            cb_data = to_cb_data(FilterKey.price, FilterKey.min)
        else:
            cb_data = to_cb_data(FilterKey.price, FilterKey.max)
        send(bot, user_id, event, markup=FilterMarkupFactory.get_param_bar_keyboard(cb_data))

    @staticmethod
    def __apply_param(user_id: int, value: str, bot: TeleBot):
        event = FilterCallback.__extract_criteria(value)
        search_param = FilterCallback.__map_event_to_search_session_param(event)
        param_value = value.split('_')[-1]
        DBController.update_search_session_params(user_id, search_param, param_value)
        FilterCallback.__show_menu(user_id, bot)

    @staticmethod
    def __close(call: CallbackQuery, bot: TeleBot):
        all_lots_cb(call, 'page_0', bot)

    @staticmethod
    def __extract_criteria(value: str) -> Event:
        if value.split('_')[0] == FilterKey.lvl.name:
            if value.split('_')[1] == FilterKey.min.name:
                return Event.input_min_lvl
            return Event.input_max_lvl
        if value.split('_')[1] == FilterKey.min.name:
            return Event.input_min_price
        return Event.input_max_price

    @staticmethod
    def __map_event_to_search_session_param(event: Event):
        if event == Event.input_min_lvl:
            return SearchSessionParam.min_lvl
        if event == Event.input_max_lvl:
            return SearchSessionParam.max_lvl
        if event == Event.input_min_price:
            return SearchSessionParam.min_price
        if event == Event.input_max_price:
            return SearchSessionParam.max_price
