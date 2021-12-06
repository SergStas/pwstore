from telebot import TeleBot
from telebot.types import CallbackQuery

from bot.utils.cb_utils import lots_list_default_handler, send_default_page, get_lot_info_args, send
from bot.utils.ui_constr import get_remove_button
from bot.utils.markup_factories import get_lots_list_default_markup_factory
from controllers.DBController import DBController
from entity.enums.Event import Event


def user_lots_cb(call: CallbackQuery, value: str, bot: TeleBot):
    lots_list_default_handler(
        bot,
        call,
        value,
        lambda l_bot, l_call, l_page: send_default_page(
            l_bot,
            l_page,
            DBController.get_user_lots(l_call.from_user.id),
            l_call.from_user.id,
            'user_lots'
        ),
        lambda lot: get_remove_button('close', lot.lot_id)
    )


# def seller_lots_cb(call: CallbackQuery, value: str, bot: TeleBot):
#     seller_id = value.split('_')[0]
#     if 'page' in value:
#         page = int(value.split('_')[2])
#         send_default_page(
#             bot=bot,
#             page=page,
#             lots=DBController.get_sellers_lots(seller_id=int(seller_id)),
#             user_id=call.from_user.id,
#             key='seller_lots',
#         )
#         return
#
#     if len(value.split('_')) > 1:
#         lot = DBController.get_lot(int(value.split('_')[1]))
#         args = get_lot_info_args(lot)
#         markup_factory = get_lots_list_default_markup_factory(
#             cb_key='seller_lots',
#             call=call,
#         )
#         send(
#             bot=bot,
#             user_id=call.from_user.id,
#             event=Event.lot_info_template,
#             args=args,
#             markup=markup_factory(lot)
#         )
#         return
#
#     lots_list_default_handler(
#         bot=bot,
#         call=call,
#         value='page_0',
#         page_switcher=lambda l_bot, l_call, l_page: send_default_page(
#             l_bot,
#             l_page,
#             DBController.get_sellers_lots(seller_id=int(value)),
#             l_call.from_user.id,
#             'seller_lots',
#         ),
#         markup_factory=get_lots_list_default_markup_factory(
#             cb_key='seller_lots',
#             call=call,
#         )
#     )
