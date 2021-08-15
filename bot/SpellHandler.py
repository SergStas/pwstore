from typing import Optional

from entity.enums.SpellEvent import SpellEvent
from logger.Logger import Logger


class SpellHandler:
    __no_arg = {
        SpellEvent.first_launch:
            'Приветствую на самой честной и бесплтаной площадке по продаже персонажей в Perfect World!\n'
            'Помни, что мы только предоставляем площадку по поиску и продаже аккаунтов. Мы не несем никакой '
            'ответственности за персонажа и ситуации после его покупки или продажи',
        SpellEvent.help:
            'Введите одну из следующих команд:\n'
            '/help - помощь\n'
            '/buy - перейти к поиску выставленных на продажу аккаунтов\n'
            '/sell - перейти в меню управления лотами продажи аккаунтов'
    }
    __with_args = {
        SpellEvent.unknown_command:
            'Команда {0} не найдена, введите /help для получения помощи'
    }

    @staticmethod
    def get_message(event: SpellEvent, args=None) -> Optional[str]:
        if event not in SpellHandler.__no_arg.keys() and \
                event not in SpellHandler.__with_args.keys():
            Logger.error(f'Spell event \'{event.name}\' not found in a dictionary')
            return None
        if event in SpellHandler.__no_arg:
            return SpellHandler.__no_arg[event]
        if args is None:
            raise Exception(f'Spell event {event.name} requires args!')
        return SpellHandler.__with_args[event].format(*args)
