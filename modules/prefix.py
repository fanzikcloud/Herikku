from core.base_module import Module


class PrefixModule(Module):
    NAME = 'Prefix Manager'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Управление префиксом команд'
    DEPENDENCIES = []
    COMMANDS = {'prefix': 'Изменить префикс команд (например: .prefix !)'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.config = config
        self.config_path = config_path

        async def prefix_handler(event):
            if not event.text or not event.text.startswith(
                f'{command_prefix}prefix'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.edit(
                    f"""**Текущий префикс:** `{command_prefix}`

Использование: `{command_prefix}prefix <новый_префикс>`"""
                    )
                return
            new_prefix = parts[1].strip()
            self.config.set('Settings', 'command_prefix', new_prefix)
            with open(self.config_path, 'w') as f:
                self.config.write(f)
            await event.edit(
                f"""✅ **Префикс изменен на:** `{new_prefix}`

⚠️ Перезапустите бота командой `{new_prefix}restart`"""
                )
        client.add_event_handler(prefix_handler, events.NewMessage(outgoing
            =True))
