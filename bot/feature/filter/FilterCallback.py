from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.feature.filter.FilterKey import FilterKey
from bot.feature.filter.FilterMarkupFactory import FilterMarkupFactory
from bot.feature.filter.FilterParams import FilterParams
from bot.utils.cb_utils import send
from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder
from entity.enums.Event import Event


class FilterCallback:
    @staticmethod
    def execute(call: CallbackQuery, value: str, bot: TeleBot):
        main_key = value.split('_')[0]
        if main_key == FilterKey.open.name:
            FilterCallback.__show_menu(call, value, bot)
        elif main_key == FilterKey.edit.name:
            FilterCallback.__edit_filter_param(call, value.split('_', 1)[1], bot)
        elif main_key == FilterKey.apply.name:
            FilterCallback.__apply_param(call, value, bot)
        elif main_key == FilterKey.close.name:
            FilterCallback.__close(call, value, bot)

    @staticmethod
    def __show_menu(call: CallbackQuery, value: str, bot: TeleBot):
        send(
            bot=bot,
            user_id=call.from_user.id,
            event=Event.filter_menu,
            markup=FilterMarkupFactory.get_filter_menu_markup(FilterParams())
        )

    @staticmethod
    def __edit_filter_param(call: CallbackQuery, value: str, bot: TeleBot):
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
        send(bot, call.from_user.id, event, markup=FilterMarkupFactory.get_param_bar_keyboard(cb_data))

    @staticmethod
    def __apply_param(call: CallbackQuery, value: str, bot: TeleBot):
        pass

    @staticmethod
    def __close(call: CallbackQuery, value: str, bot: TeleBot):
        pass

    @staticmethod
    def __extract_criteria(value: str) -> Event:
        if value.split('_')[0] == FilterKey.lvl:
            if value.split('_')[1] == FilterKey.min:
                return Event.input_min_lvl
            return Event.input_max_lvl
        if value.split('_')[1] == FilterKey.min:
            return Event.input_min_price
        return Event.input_max_price
