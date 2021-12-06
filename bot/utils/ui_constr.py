from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.feature.favs.FavsMarkup import FavsButtonArgs, FavsMarkup
from bot.spell.SpellHandler import SpellHandler
from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder
from entity.dataclass.LotData import LotData
from entity.enums.Event import Event
from entity.enums.Race import Race
from entity.enums.SellMenuOption import SellMenuOption
from entity.enums.Server import Server


def get_sell_menu_kb(cb_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text='Выставить персонажа на продажу',
        callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, SellMenuOption.new_lot.name))
    )
    kb.add(InlineKeyboardButton(
        text='Управление активными лотами',
        callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, SellMenuOption.show_lots.name))
    )
    kb.add(get_return_button())
    return kb


def get_race_select_kb(cb_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Люди', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Race.human.name)))
    kb.add(InlineKeyboardButton(text='Зооморфы', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Race.untamed.name)))
    kb.add(InlineKeyboardButton(text='Сиды', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Race.winged_elf.name)))
    kb.add(InlineKeyboardButton(text='Древние', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Race.earthguard.name)))
    kb.add(InlineKeyboardButton(text='Тени', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Race.nightshade.name)))
    kb.add(InlineKeyboardButton(text='Амфибии', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Race.tideborn.name)))
    kb.add(get_return_button())
    return kb


def get_server_selector_kb(cb_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Арктур', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Server.arcturus.name)))
    kb.add(InlineKeyboardButton(text='Скорпион', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Server.scorpion.name)))
    kb.add(InlineKeyboardButton(text='Саргас', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Server.sargaz.name)))
    kb.add(InlineKeyboardButton(text='Гиперион', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, Server.hyperion.name)))
    kb.add(get_return_button())
    return kb


def get_search_results_kb(
        lots: [LotData],
        page: int,
        cb_key: str,
        page_size: int = 10,
        value_prefix: str = ''
) -> InlineKeyboardMarkup:
    result = InlineKeyboardMarkup()
    sublist = lots[(page * page_size):][:page_size]
    for lot in sublist:
        result.add(InlineKeyboardButton(
            text=SpellHandler.get_message(
                Event.lot_info_button_template,
                (lot.char.server, lot.char.race, lot.char.lvl, lot.price)
            ),
            callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, value_prefix + str(lot.lot_id))
        ))
    b_next = InlineKeyboardButton(
        text=f'Страница #{page + 2}',
        callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, f'{value_prefix}page_{page + 1}')
    )
    b_prev = InlineKeyboardButton(
        text=f'Страница #{page}',
        callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, f'{value_prefix}page_{page - 1}')
    )
    if page > 0 and len(lots) > (page + 1) * page_size:
        result.row(b_prev, b_next)
    elif page > 0:
        result.add(b_prev)
    elif len(lots) > (page + 1) * page_size:
        result.add(b_next)
    result.add(get_return_button())
    return result


def get_remove_button(cb_key: str, lot_id: int) -> InlineKeyboardMarkup:
    close = InlineKeyboardButton(
        SpellHandler.get_message(Event.close_lot),
        callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, f'close_{lot_id}')
    )
    result = InlineKeyboardMarkup()
    result.add(close)
    result.add(get_return_button())
    return result


def get_remove_from_favs_button(lot_id: int, user_id: int, cb_key: str = 'favs') -> InlineKeyboardMarkup:
    remove = InlineKeyboardButton(
        'Удалить из избранного',
        callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, f'remove_{user_id}_{lot_id}')
    )
    result = InlineKeyboardMarkup()
    result.add(remove)
    return result


def get_remove_confirm_kb(cb_key: str, lot_id: int) -> InlineKeyboardMarkup:
    yes = InlineKeyboardButton('Принять', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, f'yes_{lot_id}'))
    no = InlineKeyboardButton('Отмена', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, f'no_{lot_id}'))
    result = InlineKeyboardMarkup()
    result.row(yes, no)
    return result


def get_main_menu_kb(cb_key: str) -> InlineKeyboardMarkup:
    buy = InlineKeyboardButton('Купить персонажа', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, 'buy'))
    sell = InlineKeyboardButton('Продать персонажа', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, 'sell'))
    favs = InlineKeyboardButton('Избранное', callback_data=CallbackKeyEncoder.enc_cb_data('favs', 'page_0'))
    result = InlineKeyboardMarkup()
    result.add(buy)
    result.row(sell, favs)
    return result


def get_return_button(cb_key: str = 'back_to_mm') -> InlineKeyboardButton:
    return InlineKeyboardButton('Вернуться в меню', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, ''))


def get_return_kb(cb_key: str = 'back_to_mm') -> InlineKeyboardMarkup:
    result = InlineKeyboardMarkup()
    result.add(get_return_button(cb_key))
    return result


def get_all_lots_markup_kb(cb_key: str, lot: LotData, is_fav: bool, page: int) -> InlineKeyboardMarkup:
    result = InlineKeyboardMarkup()
    favs = FavsMarkup.get_favs_button(
        FavsButtonArgs(adding_mode=not is_fav, lot_id=lot.lot_id)
    )
    back = __get_back_button(cb_key=cb_key, page_num=page)
    return_button = get_return_button()
    result.row(favs, back)
    result.add(return_button)
    return result

#
# def get_seller_lots_markup_kb(lot: LotData, is_fav: bool, page: int, seller_id: int) -> InlineKeyboardMarkup:
#     result = InlineKeyboardMarkup()
#     favs = FavsMarkup.get_favs_button(
#         FavsButtonArgs(lot_id=lot.lot_id, adding_mode=not is_fav)
#     )
#     back = InlineKeyboardButton(
#         text='Назад',
#         callback_data=CallbackKeyEncoder.enc_cb_data('seller_lots', f'{seller_id}_page_{page}')
#     )
#     return_button = get_return_button()
#     result.row(favs, back)
#     result.add(return_button)
#     return result


def get_all_lots_markup_kb_with_seller_lots(cb_key: str, lot: LotData, is_fav: bool, page: int) -> InlineKeyboardMarkup:
    result = InlineKeyboardMarkup()
    favs = FavsMarkup.get_favs_button(
        FavsButtonArgs(adding_mode=not is_fav, lot_id=lot.lot_id)
    )
    back = __get_back_button(cb_key=cb_key, page_num=page)
    return_button = get_return_button()
    seller_button = __get_seller_lots_button(seller_id=lot.user.user_id)
    result.row(favs, back)
    result.add(seller_button)
    result.add(return_button)
    return result


def __get_seller_lots_button(seller_id: int):
    return InlineKeyboardButton(
        'История лотов продавца',
        callback_data=CallbackKeyEncoder.enc_cb_data('seller_lots', f'{str(seller_id)}_page_0')
    )


def __get_back_button(page_num: int, cb_key: str) -> InlineKeyboardButton:
    return InlineKeyboardButton('Назад', callback_data=CallbackKeyEncoder.enc_cb_data(cb_key, f'page_{page_num}'))
