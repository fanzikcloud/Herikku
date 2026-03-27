from core.base_module import Module
from datetime import datetime
import asyncio


class PingModule(Module):
    NAME = 'Ping'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Информация о боте и время отклика'
    DEPENDENCIES = []
    COMMANDS = {'ping': 'Показать информацию о боте и время работы'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.bot_start_time = bot_start_time

        async def ping_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}ping'
                ):
                return
            start = datetime.now()
            uptime = datetime.now() - self.bot_start_time
            response = '🤖 <b>Herikku Userbot</b>\n\n'
            response += f"""⏱ <b>Время работы:</b> {uptime.days}д {uptime.seconds // 3600}ч {uptime.seconds // 60 % 60}м
"""
            response += f'📦 <b>Загружено модулей:</b> {len(loaded_modules)}\n'
            response += f'🔧 <b>Префикс:</b> <code>{self.prefix}</code>\n'
            response += f'⚡ <b>Пинг:</b> измеряю...'
            try:
                await event.edit(response)
                end = datetime.now()
                ping_time = (end - start).total_seconds() * 1000
                await asyncio.sleep(0.1)
                response = '🤖 <b>Herikku Userbot</b>\n\n'
                response += f"""⏱ <b>Время работы:</b> {uptime.days}д {uptime.seconds // 3600}ч {uptime.seconds // 60 % 60}м
"""
                response += (
                    f'📦 <b>Загружено модулей:</b> {len(loaded_modules)}\n')
                response += f'🔧 <b>Префикс:</b> <code>{self.prefix}</code>\n'
                response += f'⚡ <b>Пинг:</b> {ping_time:.2f}ms'
                await event.edit(response)
            except Exception as e:
                pass
        client.add_event_handler(ping_handler, events.NewMessage(outgoing=True)
            )
