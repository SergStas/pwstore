from entity.enums.Event import Event
from entity.enums.Race import Race


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
            'Укажите ссылку на куклу:',
        Event.new_lot_input_description:
            'Напишите описание вашего персонажа:',
        Event.new_lot_input_price:
            'Укажите цену продажи:',
        Event.new_lot_input_contacts:
            'Укажите свои контакты, с помощью которых с вами можно связаться:',
        Event.new_lot_success:
            'Персонаж успешно выставлен на продажу\n'
            'Зайдите в меню /sell чтобы просмотреть список выставленных на продажу персонажей',
        Event.new_lot_fail:
            'Возникла непредвиденная ошибка: не удалось выставить персонажа на продажу'
    }
    __with_args = {
        Event.unknown_command:
            'Команда {0} не найдена, введите /help для получения помощи',
        Event.invalid_value:
            'Значение \'{0}\' некорректно для {1}, попробуйте еще раз',
        Event.show_lots_indices:
            'Показаны лоты с {0} по {1}, страница #{2}'
    }
    __word_forms = {
        Event.filtered_lots_found:
            'По вашему запросу найден{0} {1} лот{2} персонажей'
    }
    __templates = {
        Event.lot_info_button_template:
            '[{0}] {1} ур.{2}: {3} rub',
        Event.lot_info_template:
            'Сервер: {0}\n'
            'Раса: {1}\n'
            'Уровень: {2}\n'
            'Класс: {3}\n'
            'Небо: {4}\n'
            'Кукла: {5}\n'
            '---------------------\n'
            'ЦЕНА = {6} руб.\n'
            'Продавец: @{7}\n'
            'Контактные данные продавца: {8}\n'
            'Персонаж выставлен на продажу {9}\n'
            'Описание персонажа: {10}'
    }

    @staticmethod
    def get_message(event: Event, args=None) -> str:
        if event in SpellHandler.__templates:
            return SpellHandler.__handle_template(event, args)
        if event in SpellHandler.__word_forms:
            return SpellHandler.__handle_word_forms(event, args)
        if event not in SpellHandler.__no_arg.keys() and event not in SpellHandler.__with_args.keys():
            raise Exception(f'Spell event \'{event.name}\' not found in a dictionary')
        if event in SpellHandler.__no_arg:
            return SpellHandler.__no_arg[event]
        if args is None:
            raise Exception(f'Spell event {event.name} requires args!')
        return SpellHandler.__with_args[event].format(*args)

    @staticmethod
    def __handle_word_forms(event: Event, args) -> str:
        if args is None:
            raise Exception(f'Spell event {event.name} requires args!')
        count = int(args[0])
        if event == Event.filtered_lots_found:
            format_args = ('', args[0], '',) if count == 1 else \
                ('о', args[0], 'а',) if 1 < count < 5 else \
                ('о', args[0], 'ов',)
            return SpellHandler.__word_forms[event].format(*format_args)

    @staticmethod
    def __handle_template(event: Event, args) -> str:
        if args is None:
            raise Exception(f'Template {event.name} requires args!')
        if event == Event.lot_info_button_template:
            format_args = (args[0].name.upper(), SpellHandler.__race_rus(args[1]), args[2], args[3],)
            return SpellHandler.__templates[event].format(*format_args)
        if event == Event.lot_info_template:
            format_args = (
                args[0].name.upper(),
                SpellHandler.__race_rus(args[1]).lower(),
                args[2], args[3], args[4], args[5],
                args[6], args[7], args[8], args[9], args[10],
            )
            return SpellHandler.__templates[event].format(*format_args)

    @staticmethod
    def __race_rus(race: Race) -> str:
        return 'Человек' if race == Race.human else \
            'Зооморф' if race == Race.untamed else \
            'Сид' if race == Race.winged_elf else \
            'Амфибия' if race == Race.tideborn else \
            'Древний' if race == Race.earthguard else \
            'Тень'
