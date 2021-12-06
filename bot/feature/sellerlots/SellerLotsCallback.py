from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.feature.favs.FavsMarkup import FavsMarkup, FavsButtonArgs
from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder
from bot.utils.cb_utils import send_default_page, send, get_lot_info_args, lots_list_default_handler
from bot.utils.markup_factories import get_lots_list_default_markup_factory
from bot.utils.ui_constr import get_return_button
from controllers.DBController import DBController
from entity.dataclass.LotData import LotData
from entity.enums.Event import Event


class SellerLotsCallback:
    @staticmethod
    def execute(call: CallbackQuery, value: str, bot: TeleBot):
        if 'page' in value:
            SellerLotsCallback.__handle_page_switching(call, value, bot)
        else:
            SellerLotsCallback.__handle_lot_presentation(call, value, bot)
        # else:
        #     SellerLotsCallback.__handle_lots_list(call, value, bot)

    @staticmethod
    def __handle_page_switching(call: CallbackQuery, value: str, bot: TeleBot):
        seller_id = int(value.split('_')[0])
        page = int(value.split('_')[2])
        send_default_page(
            bot=bot,
            page=page,
            lots=DBController.get_sellers_lots(seller_id=seller_id),
            user_id=call.from_user.id,
            key='seller_lots',
            value_prefix=f'{seller_id}_'
        )

    @staticmethod
    def __handle_lot_presentation(call: CallbackQuery, value: str, bot: TeleBot):
        lot = DBController.get_lot(int(value.split('_')[1]))
        args = get_lot_info_args(lot)
        markup_factory = SellerLotsCallback.__get_markup_factory(
            call=call,
            seller_id=int(value.split('_')[0])
        )
        send(
            bot=bot,
            user_id=call.from_user.id,
            event=Event.lot_info_template,
            args=args,
            markup=markup_factory(lot)
        )

    # @staticmethod
    # def __handle_lots_list(call: CallbackQuery, value: str, bot: TeleBot):
    #     lots_list_default_handler(
    #         bot=bot,
    #         call=call,
    #         value='page_0',
    #         page_switcher=lambda l_bot, l_call, l_page: send_default_page(
    #             bot=l_bot,
    #             page=l_page,
    #             lots=DBController.get_sellers_lots(seller_id=int(value)),
    #             user_id=l_call.from_user.id,
    #             key='seller_lots',
    #         ),
    #         markup_factory=SellerLotsCallback.__get_markup_factory(call=call, seller_id=int(value.split('_')[0])),
    #     )

    @staticmethod
    def __get_markup_factory(call: CallbackQuery, seller_id: int):
        return lambda l_lot: SellerLotsCallback.__get_kb(
            lot=l_lot,
            is_fav=DBController.is_fav(lot_id=l_lot.lot_id, user_id=call.from_user.id),
            page=0,
            seller_id=seller_id,
        )

    @staticmethod
    def __get_kb(lot: LotData, is_fav: bool, page: int, seller_id: int) -> InlineKeyboardMarkup:
        result = InlineKeyboardMarkup()
        favs = FavsMarkup.get_favs_button(
            FavsButtonArgs(lot_id=lot.lot_id, adding_mode=not is_fav)
        )
        back = InlineKeyboardButton(
            text='Назад',
            callback_data=CallbackKeyEncoder.enc_cb_data('seller_lots', f'{seller_id}_page_{page}')
        )
        return_button = get_return_button()
        result.row(favs, back)
        result.add(return_button)
        return result
