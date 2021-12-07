from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.feature.filter.FilterKey import FilterKey
from bot.feature.filter.FilterParams import FilterParams
from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder
from bot.utils.ui_constr import get_return_button


class FilterMarkupFactory:
    @staticmethod
    def get_param_bar_keyboard(cb_data: str) -> InlineKeyboardMarkup:
        if FilterKey.lvl.name in cb_data:
            result = FilterMarkupFactory.__get_lvl_bar_markup(cb_data)
        else:
            result = FilterMarkupFactory.__get_price_bar_markup(cb_data)
        back = FilterMarkupFactory.__get_back_button()
        back.text = 'Отмена'
        result.add(back)
        return result

    @staticmethod
    def __get_lvl_bar_markup(cb_data: str) -> InlineKeyboardMarkup:
        result = InlineKeyboardMarkup()
        result.row(
            InlineKeyboardButton(text=0, callback_data=f'{cb_data}_0'),
            InlineKeyboardButton(text=50, callback_data=f'{cb_data}_50'),
            InlineKeyboardButton(text=100, callback_data=f'{cb_data}_100'),
            InlineKeyboardButton(text=150, callback_data=f'{cb_data}_150'),
            InlineKeyboardButton(text=200, callback_data=f'{cb_data}_200'),
            InlineKeyboardButton(text=250, callback_data=f'{cb_data}_250'),
            InlineKeyboardButton(text=315, callback_data=f'{cb_data}_315'),
        )
        return result

    @staticmethod
    def __get_price_bar_markup(cb_data: str) -> InlineKeyboardMarkup:
        result = InlineKeyboardMarkup()
        result.row(
            InlineKeyboardButton(text=0, callback_data=f'{cb_data}_0'),
            InlineKeyboardButton(text=5000, callback_data=f'{cb_data}_5000'),
            InlineKeyboardButton(text=15000, callback_data=f'{cb_data}_15000'),
        )
        result.row(
            InlineKeyboardButton(text=30000, callback_data=f'{cb_data}_30000'),
            InlineKeyboardButton(text=50000, callback_data=f'{cb_data}_50000'),
            InlineKeyboardButton(text=100000, callback_data=f'{cb_data}_100000'),
        )
        return result

    @staticmethod
    def get_filter_menu_markup(state: FilterParams) -> InlineKeyboardMarkup:
        result = InlineKeyboardMarkup()
        cb_data = lambda value: CallbackKeyEncoder.enc_cb_data(FilterKey.filter.name, f'{FilterKey.edit.name}_{value}')
        min_lvl = InlineKeyboardButton(
            text=FilterMarkupFactory.__mk_text('Мин уровень', state.min_lvl),
            callback_data=cb_data(f'{FilterKey.lvl.name}_{FilterKey.min.name}'),
        )
        min_price = InlineKeyboardButton(
            text=FilterMarkupFactory.__mk_text('Мин цена', state.min_price),
            callback_data=cb_data(f'{FilterKey.price.name}_{FilterKey.min.name}'),
        )
        max_lvl = InlineKeyboardButton(
            text=FilterMarkupFactory.__mk_text('Макс уровень', state.max_lvl),
            callback_data=cb_data(f'{FilterKey.lvl.name}_{FilterKey.max.name}'),
        )
        max_price = InlineKeyboardButton(
            text=FilterMarkupFactory.__mk_text('Макс цена', state.max_price),
            callback_data=cb_data(f'{FilterKey.price.name}_{FilterKey.max.name}'),
        )
        back = FilterMarkupFactory.__get_back_button()
        result.row(min_lvl, max_lvl)
        result.row(min_price, max_price)
        result.add(back)
        result.add(get_return_button())
        return result

    @staticmethod
    def __get_back_button() -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text='Назад',
            callback_data=CallbackKeyEncoder.enc_cb_data(FilterKey.filter.name, FilterKey.close.name)
        )

    @staticmethod
    def __mk_text(label: str, value: int) -> str:
        if value is None:
            return f'{label}\n= ---'
        return f'{label}\n= {value}'
