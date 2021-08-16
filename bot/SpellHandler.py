from typing import Optional

from entity.enums.Event import Event


class SpellHandler:
    __no_arg = {
        Event.first_launch:
            'Приветствую на самой честной и бесплтаной площадке по продаже персонажей в Perfect World!\n'
            'Помни, что мы только предоставляем площадку по поиску и продаже аккаунтов. Мы не несем никакой '
            'ответственности за персонажа и ситуации после его покупки или продажи\n\n'
            'Введите /help чтобы получить справку',
        Event.help:
            'Введите одну из следующих команд:\n'
            '/help - помощь\n'
            '/buy - перейти к поиску выставленных на продажу аккаунтов\n'
            '/sell - перейти в меню управления выставленными на продажу аккаунтов',
        Event.search_select_server:
            'Выберите нужный вам сервер',
        Event.search_select_race:
            'Выберите нужную вам расу',
        Event.no_lots_found:
            'Персонажей по вашему запросу не найдено, попробуйте другие настройки\n'
            'Введите /buy чтобы выбрать параметры еще раз',
        Event.db_error:
            'Произошла ошибка, информация об активных лотах не найдена',
        Event.sell_menu:
            'Что вы хотите сделать?',
        Event.new_lot_input_server:
            'Укажите сервер вашего персонажа:',
        Event.new_lot_input_race:
            'Укажите расу:',
        Event.new_lot_input_class:
            'Введите класс вашего персонажа:',
        Event.new_lot_input_lvl:
            'Введите уровень вашего персонажа:',
        Event.new_lot_input_heaven:
            'Укажите уровень неба вашего персонажа:',
        Event.new_lot_input_doll:
            'Укажите смылку на куклу:',
        Event.new_lot_input_description:
            'Напишите описание вашего персонажа:',
        Event.new_lot_input_price:
            'Укажите цену продажи:',
        Event.new_lot_input_contacts:
            'Укажите свои контакты, с помощью которых с вами можно связаться:',
    }
    __with_args = {
        Event.unknown_command:
            'Команда {0} не найдена, введите /help для получения помощи',
        Event.invalid_value:
            'Значение \'{0}\' некорректно для {1}, попробуйте еще раз'
    }
    __special = {
        Event.filtered_lots_found:
            'По вашему запросу найден{0} {1} лот{2} персонажей'
    }

    @staticmethod
    def get_message(event: Event, args=None) -> str:
        if event in SpellHandler.__special:
            return SpellHandler.handle_special(event, args)
        if event not in SpellHandler.__no_arg.keys() and event not in SpellHandler.__with_args.keys():
            raise Exception(f'Spell event \'{event.name}\' not found in a dictionary')
        if event in SpellHandler.__no_arg:
            return SpellHandler.__no_arg[event]
        if args is None:
            raise Exception(f'Spell event {event.name} requires args!')
        return SpellHandler.__with_args[event].format(*args)

    @staticmethod
    def handle_special(event: Event, args) -> Optional[str]:
        if args is None:
            raise Exception(f'Spell event {event.name} requires args!')
        count = int(args[0])
        if event == Event.filtered_lots_found:
            format_args = ('', args[0], '',) if count == 1 else \
                ('о', args[0], 'а',) if 1 < count < 5 else \
                ('о', args[0], 'ов',)
            return SpellHandler.__special[event].format(*format_args)

