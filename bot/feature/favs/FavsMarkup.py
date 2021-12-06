from telebot.types import InlineKeyboardButton

from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder


class FavsButtonArgs:
    def __init__(
            self,
            lot_id: int,
            adding_mode: bool,
    ):
        self.lot_id = lot_id
        self.adding_mode = adding_mode


class FavsMarkup:
    @staticmethod
    def get_favs_button(args: FavsButtonArgs) -> InlineKeyboardButton:
        if args.adding_mode:
            label = "Добавить в избранное"
            cb_key = CallbackKeyEncoder.enc_void('favs', f'add_{args.lot_id}')
        else:
            label = "Удалить из избранного"
            cb_key = CallbackKeyEncoder.enc_void('favs', f'remove_{args.lot_id}')
        return InlineKeyboardButton(text=label, callback_data=cb_key)
