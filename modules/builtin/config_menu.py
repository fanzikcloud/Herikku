from core.base_module import Module


class ConfigMenuModule(Module):
    NAME = 'Config Menu'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Inline-меню для настройки юзербота'
    DEPENDENCIES = []
    COMMANDS = {'config': 'Открыть меню настроек через inline-бота'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.loaded_modules = loaded_modules

        async def config_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}config'):
                return
            bot_username = self.config.get('InlineBot', 'username', fallback=''
                )
            bot_token = self.config.get('InlineBot', 'token', fallback='')
            if not bot_username or not bot_token:
                await event.edit(
                    '❌ Inline-бот не настроен. Перезапустите юзербот для автоматической настройки.'
                    )
                return
            try:
                bot = await self.client.get_entity(bot_username)
                result = await self.client.inline_query(bot, 'config')
                await result[0].click(event.chat_id, reply_to=event.
                    reply_to_msg_id)
                await event.delete()
            except Exception as e:
                await event.edit(
                    f"""❌ Ошибка вызова inline-меню: {str(e)}

Попробуйте написать боту @{bot_username} напрямую или используйте команду: `@{bot_username} config`"""
                    )
        client.add_event_handler(config_handler, events.NewMessage(outgoing
            =True))
