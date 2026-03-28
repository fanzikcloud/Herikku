from core.base_module import Module
from core.formatting import text_formatter
from core.permissions import permission_manager


class HelpModule(Module):
    NAME = 'Help'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Показывает список доступных модулей и команд'
    DEPENDENCIES = []
    COMMANDS = {'help': 'Показать список всех модулей и команд'}

    @staticmethod
    async def INLINE_HANDLERS(bot_client, events, config, loaded_modules):
        from telethon import Button
        from core.formatting import text_formatter
        from core.permissions import permission_manager
        owner_id = None

        @bot_client.on(events.InlineQuery)
        async def help_inline_query(event):
            nonlocal owner_id
            query = event.text.strip().lower()
            if query != 'help':
                return
            if owner_id is None:
                owner_id = event.sender_id
            if event.sender_id != owner_id:
                await event.answer([])
                return
            builder = event.builder
            prefix = config.get('Settings', 'command_prefix', fallback='.')
            modules_list = list(loaded_modules.items())
            items_per_page = 3
            total_pages = (len(modules_list) + items_per_page - 1
                ) // items_per_page
            fmt = text_formatter
            response = fmt.header(owner_id, 'Herikku Userbot - Модули', 'robot'
                )
            response += '\n\n'
            response += fmt.info(owner_id,
                f'Префикс команд: <code>{prefix}</code>')
            response += '\n'
            if total_pages > 1:
                response += fmt.info(owner_id, f'Страница 1/{total_pages}')
                response += '\n'
            response += '\n'
            for module_name, module_instance in modules_list[:items_per_page]:
                can_use = permission_manager.can_use_module(owner_id,
                    module_name)
                status_emoji = fmt.emoji(owner_id, 'success'
                    ) if can_use else fmt.emoji(owner_id, 'error')
                response += f'{status_emoji} <b>{module_instance.NAME}</b>\n'
                response += (
                    f"   {fmt.emoji(owner_id, 'info')} Автор: {module_instance.AUTHOR}\n"
                    )
                response += (
                    f"   {fmt.emoji(owner_id, 'book')} {module_instance.DESCRIPTION}\n"
                    )
                if module_instance.COMMANDS:
                    response += (
                        f"   {fmt.emoji(owner_id, 'gear')} <b>Команды:</b>\n")
                    for cmd, desc in module_instance.COMMANDS.items():
                        cmd_can_use = permission_manager.can_use_command(
                            owner_id, cmd)
                        cmd_emoji = fmt.bullet(owner_id, 'check'
                            ) if cmd_can_use else fmt.bullet(owner_id, 'cross')
                        response += (
                            f'      {cmd_emoji} <code>{prefix}{cmd}</code> - {desc}\n'
                            )
                response += '\n'
            buttons = []
            if total_pages > 1:
                buttons.append([Button.inline('➡️ Далее', b'help_page_2')])
            result = builder.article(title='📚 Список модулей', text=
                response, buttons=buttons if buttons else None)
            await event.answer([result])

        @bot_client.on(events.CallbackQuery(pattern=b'help_page_'))
        async def help_pagination_handler(event):
            if owner_id is not None and event.sender_id != owner_id:
                await event.answer('❌ Эти кнопки не для вас!', alert=True)
                return
            page_num = int(event.data.decode('utf-8').split('_')[-1])
            modules_list = list(loaded_modules.items())
            items_per_page = 3
            total_pages = (len(modules_list) + items_per_page - 1
                ) // items_per_page
            if page_num < 1 or page_num > total_pages:
                await event.answer('❌ Страница не найдена', alert=True)
                return
            start_idx = (page_num - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_modules = modules_list[start_idx:end_idx]
            prefix = config.get('Settings', 'command_prefix', fallback='.')
            fmt = text_formatter
            response = fmt.header(owner_id, 'Herikku Userbot - Модули', 'robot'
                )
            response += '\n\n'
            response += fmt.info(owner_id,
                f'Префикс команд: <code>{prefix}</code>')
            response += '\n'
            response += fmt.info(owner_id, f'Страница {page_num}/{total_pages}'
                )
            response += '\n\n'
            for module_name, module_instance in page_modules:
                can_use = permission_manager.can_use_module(owner_id,
                    module_name)
                status_emoji = fmt.emoji(owner_id, 'success'
                    ) if can_use else fmt.emoji(owner_id, 'error')
                response += f'{status_emoji} <b>{module_instance.NAME}</b>\n'
                response += (
                    f"   {fmt.emoji(owner_id, 'info')} Автор: {module_instance.AUTHOR}\n"
                    )
                response += (
                    f"   {fmt.emoji(owner_id, 'book')} {module_instance.DESCRIPTION}\n"
                    )
                if module_instance.COMMANDS:
                    response += (
                        f"   {fmt.emoji(owner_id, 'gear')} <b>Команды:</b>\n")
                    for cmd, desc in module_instance.COMMANDS.items():
                        cmd_can_use = permission_manager.can_use_command(
                            owner_id, cmd)
                        cmd_emoji = fmt.bullet(owner_id, 'check'
                            ) if cmd_can_use else fmt.bullet(owner_id, 'cross')
                        response += (
                            f'      {cmd_emoji} <code>{prefix}{cmd}</code> - {desc}\n'
                            )
                response += '\n'
            buttons = []
            nav_buttons = []
            if page_num > 1:
                nav_buttons.append(Button.inline('⬅️ Назад',
                    f'help_page_{page_num - 1}'.encode('utf-8')))
            if page_num < total_pages:
                nav_buttons.append(Button.inline('➡️ Далее',
                    f'help_page_{page_num + 1}'.encode('utf-8')))
            if nav_buttons:
                buttons.append(nav_buttons)
            await event.edit(response, buttons=buttons if buttons else None)

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config

        async def help_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}help'
                ):
                return
            me = await self.client.get_me()
            user_id = me.id
            bot_username = self.config.get('InlineBot', 'username', fallback=''
                )
            bot_token = self.config.get('InlineBot', 'token', fallback='')
            if not bot_username or not bot_token:
                text = text_formatter.error(user_id,
                    'Inline-бот не настроен. Перезапустите юзербот для автоматической настройки.'
                    )
                await event.edit(text)
                return
            try:
                bot = await self.client.get_entity(bot_username)
                result = await self.client.inline_query(bot, 'help')
                await result[0].click(event.chat_id, reply_to=event.
                    reply_to_msg_id)
                await event.delete()
            except Exception as e:
                fmt = text_formatter
                text = fmt.error(user_id,
                    f'Ошибка вызова inline-меню: {str(e)}')
                text += '\n\n'
                text += fmt.info(user_id,
                    f'Попробуйте написать боту @{bot_username} напрямую или используйте команду: `@{bot_username} help`'
                    )
                await event.edit(text)
        client.add_event_handler(help_handler, events.NewMessage(outgoing=True)
            )
