from core.base_module import Module
from datetime import datetime
import asyncio
from core.formatting import markdown_to_html


class PingModule(Module):
    NAME = 'Ping'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Информация о боте и время отклика (с настраиваемым шаблоном)'
    DEPENDENCIES = []
    COMMANDS = {
        'ping': 'Показать информацию о боте и время работы',
        'setping <текст>': 'Настроить шаблон для команды ping'
    }
    CONFIG_ICON = '⚡'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_ping':
            ping_text = config.get('Ping', 'text', fallback='не установлен')
            text = '<b>⚡ Ping - Настройки</b>\n\n'
            text += f'📝 <b>Текущий шаблон:</b>\n{ping_text}\n\n'
            text += '<b>Команды для настройки:</b>\n'
            text += f'• <code>.setping &lt;текст&gt;</code> - изменить шаблон\n\n'
            text += '<b>Доступные плейсхолдеры:</b>\n'
            text += '• <code>{ping}</code> - пинг в ms\n'
            text += '• <code>{uptime}</code> - время работы бота\n'
            text += '• <code>{modules}</code> - количество загруженных модулей\n'
            text += '• <code>{prefix}</code> - текущий префикс\n\n'
            text += '<b>Поддерживается форматирование:</b>\n'
            text += '• Markdown (жирный, курсив, код, цитаты)'
            buttons = [[Button.inline('◀️ К модулям', b'settings_modules')]]
            await event.edit(text, buttons=buttons)
        else:
            raise Exception('Not our callback')

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.config_path = config_path
        self.loaded_modules = loaded_modules
        self.bot_start_time = bot_start_time

        if not config.has_section('Ping'):
            config.add_section('Ping')
            config.set('Ping', 'text',
                """🤖 **Herikku Userbot**

⏱ **Время работы:** {uptime}
📦 **Загружено модулей:** {modules}
🔧 **Префикс:** `{prefix}`
⚡ **Пинг:** {ping}ms"""
                )
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)

        async def ping_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}ping'):
                return
            start = datetime.now()
            
            # Временное сообщение для замера пинга
            await event.edit('⚡ `измеряю пинг...`')
            end = datetime.now()
            ping_time = (end - start).total_seconds() * 1000
            
            uptime = datetime.now() - self.bot_start_time
            uptime_str = f'{uptime.days}д {uptime.seconds // 3600}ч {uptime.seconds // 60 % 60}м'
            
            # Получаем шаблон
            ping_template = self.config.get('Ping', 'text', fallback='⚡ Пинг: {ping}ms')
            
            # Производим подстановку плейсхолдеров
            for placeholder, value in [
                ('ping', f'{ping_time:.2f}'),
                ('uptime', uptime_str),
                ('modules', str(len(self.loaded_modules))),
                ('prefix', self.prefix)
            ]:
                ping_template = ping_template.replace(f'{{{placeholder}}}', value)
                ping_template = ping_template.replace(f'{{{{{placeholder}}}}}', value)
                
            # Парсим форматирование
            ping_template = markdown_to_html(ping_template)
            
            await event.edit(ping_template)

        async def setping_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}setping'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                current_text = self.config.get('Ping', 'text', fallback='не установлен')
                await event.edit(
                    f"""**📝 Текущий шаблон ping:**
{current_text}

**Использование:**
<code>{self.prefix}setping &lt;текст&gt;</code>

**Доступные плейсхолдеры:**
• <code>{{ping}}</code> - пинг в ms
• <code>{{uptime}}</code> - время работы
• <code>{{modules}}</code> - кол-во модулей
• <code>{{prefix}}</code> - префикс бота"""
                )
                return
            new_text = parts[1]
            self.config.set('Ping', 'text', new_text)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            await event.edit(f'✅ Шаблон ping успешно изменен!\n\n<b>Предпросмотр:</b>\n{new_text}')

        client.add_event_handler(ping_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(setping_handler, events.NewMessage(outgoing=True))
