import datetime
import time

from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.cb_utils import send
from bot.utils.CallbackKeyEncoder import CallbackKeyEncoder
from bot.utils.ui_constr import get_return_kb, get_return_button
from controllers.DBController import DBController
from entity.enums.Event import Event


class LotVisitCallback:
    @staticmethod
    def execute(call: CallbackQuery, value: str, bot: TeleBot):
        user_id = call.from_user.id

        if 'date' in value:
            if '_' not in value:
                LotVisitCallback.__process_date_selection_query(bot, user_id)
            else:
                LotVisitCallback.__list_lots_visits(bot, user_id, int(value.split('_')[1]))

    @staticmethod
    def __list_lots_visits(bot: TeleBot, user_id: int, ts: int):
        lots_visits = DBController.get_visits_summary(user_id, datetime.date.fromtimestamp(ts))
        text = ''
        for lv in lots_visits:
            if text != '':
                text += ',\n'
            text += f'{lv.lot.char.race.name[:1].upper()}{lv.lot.char.race.name[1:]} ' \
                    f'{lv.lot.char.lvl} lvl ({lv.lot.char.server.name[:3].upper()}): {lv.visits_count} раз'
        if len(lots_visits) == 0:
            text = 'У вас нет активных лотов'
        markup = get_return_kb()
        send(
            bot=bot,
            user_id=user_id,
            event=Event.lots_visit_data,
            args=(datetime.date.fromtimestamp(ts).strftime('%d.%m.%y'), text,),
            markup=markup,
        )

    @staticmethod
    def __process_date_selection_query(bot: TeleBot, user_id: int):
        markup = LotVisitCallback.__get_date_selection_markup()
        send(
            bot=bot,
            user_id=user_id,
            event=Event.select_date,
            markup=markup
        )

    @staticmethod
    def __get_date_selection_markup() -> InlineKeyboardMarkup:
        result = InlineKeyboardMarkup()
        to_timestamp = lambda days_delta: \
            int(time.mktime((datetime.date.today() +
                             datetime.timedelta(days=-days_delta))
                            .timetuple()))
        to_cb_data = lambda ts: CallbackKeyEncoder.enc_cb_data('lot_visit', f'date_{ts}')
        ts_today = to_timestamp(1)
        ts_week = to_timestamp(7)
        ts_month = to_timestamp(30)
        ts_all = 1

        today = InlineKeyboardButton(text='За день', callback_data=to_cb_data(ts_today))
        week = InlineKeyboardButton(text='За 7 дней', callback_data=to_cb_data(ts_week))
        month = InlineKeyboardButton(text='За 30 дней', callback_data=to_cb_data(ts_month))
        all_time = InlineKeyboardButton(text='За все время', callback_data=to_cb_data(ts_all))
        return_button = get_return_button()

        result.row(today, week)
        result.row(month, all_time)
        result.add(return_button)

        return result
