from telebot.types import CallbackQuery

from bot.utils.ui_constr import get_all_lots_markup_kb, get_all_lots_markup_kb_with_seller_lots
from controllers.DBController import DBController


def get_lots_list_default_markup_factory(cb_key: str, call, with_seller_lots: bool = False):
    if with_seller_lots:
        result = lambda l_lot: get_all_lots_markup_kb_with_seller_lots(
                cb_key=cb_key,
                lot=l_lot,
                is_fav=DBController.is_fav(lot_id=l_lot.lot_id, user_id=call.from_user.id),
                page=0
            )
    else:
        result = lambda l_lot: get_all_lots_markup_kb(
                cb_key=cb_key,
                lot=l_lot,
                is_fav=DBController.is_fav(lot_id=l_lot.lot_id, user_id=call.from_user.id),
                page=0
            )
    return result


def get_seller_lots_markup_factory(call: CallbackQuery):
    result = lambda l_lot: a(
            cb_key='seller_lots',
            lot=l_lot,
            is_fav=DBController.is_fav(lot_id=l_lot.lot_id, user_id=call.from_user.id),
            page=0
        )
    return result
