from core.base_module import Module
from core.permissions import permission_manager
from core.formatting import text_formatter


class PermissionsManagerModule(Module):
    NAME = 'Permissions Manager'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Управление правами доступа для аккаунтов'
    DEPENDENCIES = []
    COMMANDS = {'perms': 'Управление правами (.perms help для справки)',
        'setmain': 'Установить главный аккаунт (только один раз)'}
    CONFIG_ICON = '🔐'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_permissions_manager':
            text = '<b>🔐 Permissions Manager</b>\n\n'
            text += (
                '<b>Система управления правами доступа для мультиаккаунтов</b>\n\n'
                )
            text += '<b>📌 Как это работает:</b>\n'
            text += (
                '1. Установите главный аккаунт командой <code>.setmain</code>\n'
                )
            text += '2. Главный аккаунт получает полный контроль\n'
            text += (
                '3. Ограничивайте доступ других аккаунтов к командам/модулям\n'
                )
            text += '4. Все изменения сохраняются автоматически\n\n'
            text += '<b>🎯 Основные команды:</b>\n'
            text += (
                '• <code>.setmain</code> - установить главный аккаунт (только один раз!)\n'
                )
            text += (
                '• <code>.perms help</code> - подробная справка по всем командам\n'
                )
            text += (
                '• <code>.perms list</code> - список всех аккаунтов с правами\n'
                )
            text += """• <code>.perms info &lt;user_id&gt;</code> - детальная информация об аккаунте

"""
            text += '<b>🚫 Ограничение доступа:</b>\n'
            text += """• <code>.perms disable &lt;user_id&gt; &lt;command&gt;</code> - запретить команду
"""
            text += """• <code>.perms enable &lt;user_id&gt; &lt;command&gt;</code> - разрешить команду
"""
            text += """• <code>.perms dismod &lt;user_id&gt; &lt;module&gt;</code> - отключить весь модуль
"""
            text += """• <code>.perms enmod &lt;user_id&gt; &lt;module&gt;</code> - включить модуль

"""
            text += '<b>💡 Примеры использования:</b>\n'
            text += '<pre>\n'
            text += '.perms disable 123456789 terminal\n'
            text += '.perms dismod 987654321 backup\n'
            text += '.perms info 123456789\n'
            text += '</pre>\n\n'
            text += '<b>⚠️ Важные правила:</b>\n'
            text += '• Только главный аккаунт может управлять правами\n'
            text += '• Главный аккаунт нельзя ограничить\n'
            text += """• Изменить главный аккаунт можно только вручную в <code>permissions.json</code>
"""
            text += '• Узнать ID аккаунтов: <code>.checkaccounts</code>\n\n'
            text += (
                '📖 <b>Полная документация:</b> <code>PERMISSIONS_GUIDE.md</code>'
                )
            buttons = [[Button.inline('◀️ К модулям', b'settings_modules')]]
            await event.edit(text, buttons=buttons)
        else:
            raise Exception('Not our callback')

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.loaded_modules = loaded_modules

        async def perms_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}perms'):
                return
            me = await self.client.get_me()
            user_id = me.id
            parts = event.text.split()
            if len(parts) == 1 or parts[1] == 'help':
                fmt = text_formatter
                text = fmt.header(user_id, 'Permissions Manager - Справка',
                    'lock')
                text += '\n\n'
                text += fmt.section(user_id, '📋 Основные команды',
                    f"""{fmt.list_item(user_id, f'`{self.prefix}perms list` - показать все аккаунты с правами', 'arrow')}
{fmt.list_item(user_id, f'`{self.prefix}perms info <user_id>` - детальная информация об аккаунте', 'arrow')}
{fmt.list_item(user_id, f'`{self.prefix}setmain` - установить главный аккаунт (один раз)', 'arrow')}"""
                    , 'info')
                text += fmt.section(user_id, '🚫 Отключение команд',
                    f"""{fmt.list_item(user_id, f'`{self.prefix}perms disable <user_id> <command>`', 'cross')}
Пример: `{self.prefix}perms disable 123456789 terminal`
Отключает команду terminal для указанного аккаунта"""
                    , 'error')
                text += fmt.section(user_id, '✅ Включение команд',
                    f"""{fmt.list_item(user_id, f'`{self.prefix}perms enable <user_id> <command>`', 'check')}
Пример: `{self.prefix}perms enable 123456789 terminal`
Включает обратно отключенную команду"""
                    , 'success')
                text += fmt.section(user_id, '📦 Управление модулями',
                    f"""{fmt.list_item(user_id, f'`{self.prefix}perms dismod <user_id> <module>` - отключить модуль', 'cross')}
{fmt.list_item(user_id, f'`{self.prefix}perms enmod <user_id> <module>` - включить модуль', 'check')}
Пример: `{self.prefix}perms dismod 123456789 backup`"""
                    , 'package')
                text += '\n' + fmt.warning(user_id,
                    'Только главный аккаунт может управлять правами!')
                text += '\n' + fmt.info(user_id,
                    f'Узнать ID аккаунта: `{self.prefix}checkaccounts`')
                text += '\n\n' + fmt.emoji(user_id, 'book'
                    ) + ' **Полная документация:** `PERMISSIONS_GUIDE.md`'
                await event.edit(text)
                return
            if not permission_manager.is_main_account(user_id):
                text = text_formatter.error(user_id,
                    'У вас нет прав для управления правами!')
                text += '\n\n' + text_formatter.info(user_id,
                    'Только главный аккаунт может использовать эту команду')
                await event.edit(text)
                return
            command = parts[1]
            if command == 'list':
                accounts = permission_manager.get_all_accounts()
                fmt = text_formatter
                if not accounts:
                    text = fmt.warning(user_id,
                        'Нет зарегистрированных аккаунтов')
                    text += '\n\n' + fmt.info(user_id,
                        f'Используйте `{self.prefix}setmain` для установки главного аккаунта'
                        )
                    await event.edit(text)
                    return
                text = fmt.header(user_id, 'Список аккаунтов с правами',
                    'shield')
                text += '\n\n'
                for acc_id, acc_data in accounts.items():
                    role = acc_data.get('role', 'user')
                    role_emoji = fmt.emoji(user_id, 'crown'
                        ) if role == 'owner' else fmt.emoji(user_id, 'key')
                    text += (
                        f'{role_emoji} **ID:** `{acc_id}` | **Роль:** `{role}`\n'
                        )
                    disabled_cmds = acc_data.get('disabled_commands', [])
                    disabled_mods = acc_data.get('disabled_modules', [])
                    if disabled_cmds:
                        text += f"""  {fmt.emoji(user_id, 'error')} Отключено команд: {len(disabled_cmds)}
"""
                    if disabled_mods:
                        text += f"""  {fmt.emoji(user_id, 'error')} Отключено модулей: {len(disabled_mods)}
"""
                    if not disabled_cmds and not disabled_mods:
                        text += (
                            f"  {fmt.emoji(user_id, 'success')} Полный доступ\n"
                            )
                    text += '\n'
                text += fmt.info(user_id,
                    f'Используйте `{self.prefix}perms info <user_id>` для подробностей'
                    )
                await event.edit(text)
            elif command == 'disable' and len(parts) >= 4:
                try:
                    target_id = int(parts[2])
                    cmd = parts[3]
                    if permission_manager.is_main_account(target_id):
                        text = text_formatter.error(user_id,
                            'Нельзя ограничить главный аккаунт!')
                        await event.edit(text)
                        return
                    permission_manager.add_account(target_id)
                    permission_manager.disable_command(target_id, cmd)
                    text = text_formatter.success(user_id,
                        f'Команда `{cmd}` отключена для аккаунта `{target_id}`'
                        )
                    text += '\n\n' + text_formatter.info(user_id,
                        f'Проверить: `{self.prefix}perms info {target_id}`')
                    await event.edit(text)
                except ValueError:
                    text = text_formatter.error(user_id,
                        'Неверный формат ID аккаунта')
                    text += '\n\n' + text_formatter.info(user_id,
                        f'Использование: `{self.prefix}perms disable <user_id> <command>`'
                        )
                    await event.edit(text)
            elif command == 'enable' and len(parts) >= 4:
                try:
                    target_id = int(parts[2])
                    cmd = parts[3]
                    permission_manager.enable_command(target_id, cmd)
                    text = text_formatter.success(user_id,
                        f'Команда `{cmd}` включена для аккаунта `{target_id}`')
                    await event.edit(text)
                except ValueError:
                    text = text_formatter.error(user_id,
                        'Неверный формат ID аккаунта')
                    await event.edit(text)
            elif command == 'dismod' and len(parts) >= 4:
                try:
                    target_id = int(parts[2])
                    mod = parts[3]
                    if permission_manager.is_main_account(target_id):
                        text = text_formatter.error(user_id,
                            'Нельзя ограничить главный аккаунт!')
                        await event.edit(text)
                        return
                    permission_manager.add_account(target_id)
                    permission_manager.disable_module(target_id, mod)
                    text = text_formatter.success(user_id,
                        f'Модуль `{mod}` отключен для аккаунта `{target_id}`')
                    text += '\n\n' + text_formatter.warning(user_id,
                        'Все команды этого модуля теперь недоступны')
                    await event.edit(text)
                except ValueError:
                    text = text_formatter.error(user_id,
                        'Неверный формат ID аккаунта')
                    await event.edit(text)
            elif command == 'enmod' and len(parts) >= 4:
                try:
                    target_id = int(parts[2])
                    mod = parts[3]
                    permission_manager.enable_module(target_id, mod)
                    text = text_formatter.success(user_id,
                        f'Модуль `{mod}` включен для аккаунта `{target_id}`')
                    await event.edit(text)
                except ValueError:
                    text = text_formatter.error(user_id,
                        'Неверный формат ID аккаунта')
                    await event.edit(text)
            elif command == 'info' and len(parts) >= 3:
                try:
                    target_id = int(parts[2])
                    fmt = text_formatter
                    role = permission_manager.get_role(target_id)
                    disabled_cmds = permission_manager.get_disabled_commands(
                        target_id)
                    disabled_mods = permission_manager.get_disabled_modules(
                        target_id)
                    text = fmt.header(user_id,
                        f'Информация об аккаунте {target_id}', 'info')
                    text += '\n\n'
                    role_emoji = fmt.emoji(user_id, 'crown'
                        ) if role == 'owner' else fmt.emoji(user_id, 'key')
                    text += f'{role_emoji} **Роль:** `{role}`\n'
                    if role == 'owner':
                        text += fmt.emoji(user_id, 'star') + """ Главный аккаунт - полный доступ ко всем функциям
"""
                    text += '\n'
                    if disabled_cmds:
                        text += fmt.section(user_id, 'Отключенные команды',
                            '\n'.join([fmt.list_item(user_id, f'`{cmd}`',
                            'cross') for cmd in disabled_cmds]), 'error')
                        text += fmt.info(user_id,
                            f'Включить: `{self.prefix}perms enable {target_id} <command>`'
                            )
                        text += '\n\n'
                    if disabled_mods:
                        text += fmt.section(user_id, 'Отключенные модули',
                            '\n'.join([fmt.list_item(user_id, f'`{mod}`',
                            'cross') for mod in disabled_mods]), 'error')
                        text += fmt.info(user_id,
                            f'Включить: `{self.prefix}perms enmod {target_id} <module>`'
                            )
                        text += '\n\n'
                    if (not disabled_cmds and not disabled_mods and role !=
                        'owner'):
                        text += fmt.success(user_id,
                            'Все команды и модули доступны')
                    await event.edit(text)
                except ValueError:
                    text = text_formatter.error(user_id,
                        'Неверный формат ID аккаунта')
                    await event.edit(text)
            else:
                text = text_formatter.error(user_id,
                    f'Неизвестная команда: `{command}`')
                text += '\n\n' + text_formatter.info(user_id,
                    f'Используйте `{self.prefix}perms help` для справки')
                await event.edit(text)

        async def setmain_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}setmain'):
                return
            me = await self.client.get_me()
            user_id = me.id
            if permission_manager.main_account_id is not None:
                fmt = text_formatter
                text = fmt.error(user_id,
                    f'Главный аккаунт уже установлен: `{permission_manager.main_account_id}`'
                    )
                text += '\n\n'
                text += fmt.warning(user_id,
                    'Изменить главный аккаунт можно только вручную:')
                text += '\n'
                text += fmt.list_item(user_id,
                    '1. Откройте файл `permissions.json`', 'arrow')
                text += '\n'
                text += fmt.list_item(user_id,
                    '2. Измените `main_account_id`', 'arrow')
                text += '\n'
                text += fmt.list_item(user_id,
                    f'3. Перезапустите бота: `{self.prefix}restart`', 'arrow')
                await event.edit(text)
                return
            permission_manager.set_main_account(user_id)
            fmt = text_formatter
            text = fmt.header(user_id, 'Главный аккаунт установлен!', 'crown')
            text += '\n\n'
            text += fmt.success(user_id,
                f'Вы ({user_id}) теперь главный аккаунт!')
            text += '\n\n'
            text += fmt.section(user_id, 'Ваши возможности',
                f"""{fmt.list_item(user_id, 'Управление правами других аккаунтов', 'check')}
{fmt.list_item(user_id, 'Отключение команд и модулей', 'check')}
{fmt.list_item(user_id, 'Полный доступ ко всем функциям', 'check')}"""
                , 'star')
            text += '\n'
            text += fmt.info(user_id,
                f'Начните с команды: `{self.prefix}perms help`')
            await event.edit(text)
        client.add_event_handler(perms_handler, events.NewMessage(outgoing=
            True))
        client.add_event_handler(setmain_handler, events.NewMessage(
            outgoing=True))
