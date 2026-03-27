from core.base_module import Module
import time
from collections import defaultdict


class AntiSpamModule(Module):
    NAME = 'AntiSpam'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Автоматическая блокировка спамеров в личных сообщениях'
    DEPENDENCIES = []
    COMMANDS = {'antispam': 'Включить/выключить антиспам защиту',
        'antispam status': 'Показать статус и статистику',
        'antispam whitelist <ID>': 'Добавить пользователя в белый список',
        'antispam unwhitelist <ID>': 'Убрать пользователя из белого списка'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.config_path = config_path
        self.enabled = config.getboolean('AntiSpam', 'enabled', fallback=False)
        self.max_messages = config.getint('AntiSpam', 'max_messages',
            fallback=5)
        self.time_window = config.getint('AntiSpam', 'time_window', fallback=10
            )
        whitelist_str = config.get('AntiSpam', 'whitelist', fallback='')
        self.whitelist = set(int(x.strip()) for x in whitelist_str.split(
            ',') if x.strip())
        self.message_history = defaultdict(list)
        self.blocked_users = set()
        self.total_blocked = 0
        if not config.has_section('AntiSpam'):
            config.add_section('AntiSpam')
            config.set('AntiSpam', 'enabled', str(self.enabled))
            config.set('AntiSpam', 'max_messages', str(self.max_messages))
            config.set('AntiSpam', 'time_window', str(self.time_window))
            config.set('AntiSpam', 'whitelist', '')
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)

        async def antispam_command_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}antispam'):
                return
            args = event.text.split()
            if len(args) == 1:
                self.enabled = not self.enabled
                self.config.set('AntiSpam', 'enabled', str(self.enabled))
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                status = '✅ Включен' if self.enabled else '❌ Выключен'
                await event.edit(
                    f"""**🛡 AntiSpam**

{status}

Спамеры будут автоматически блокироваться при отправке более {self.max_messages} сообщений за {self.time_window} секунд."""
                    )
            elif len(args) == 2 and args[1].lower() == 'status':
                status = '✅ Включен' if self.enabled else '❌ Выключен'
                message = f'**🛡 AntiSpam - Статус**\n\n'
                message += f'Состояние: {status}\n'
                message += (
                    f'Лимит: {self.max_messages} сообщений за {self.time_window} сек\n'
                    )
                message += f'Заблокировано всего: {self.total_blocked}\n'
                message += (
                    f'Белый список: {len(self.whitelist)} пользователей\n\n')
                if self.blocked_users:
                    message += f'**Заблокированные в этой сессии:**\n'
                    for user_id in list(self.blocked_users)[:5]:
                        message += f'• `{user_id}`\n'
                    if len(self.blocked_users) > 5:
                        message += (
                            f'• ... и еще {len(self.blocked_users) - 5}\n')
                await event.edit(message)
            elif len(args) == 3 and args[1].lower() == 'whitelist':
                try:
                    user_id = int(args[2])
                    self.whitelist.add(user_id)
                    whitelist_str = ','.join(str(x) for x in self.whitelist)
                    self.config.set('AntiSpam', 'whitelist', whitelist_str)
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        self.config.write(f)
                    await event.edit(
                        f"""**🛡 AntiSpam**

✅ Пользователь `{user_id}` добавлен в белый список"""
                        )
                except ValueError:
                    await event.edit(
                        f'**🛡 AntiSpam**\n\n❌ Неверный ID пользователя')
            elif len(args) == 3 and args[1].lower() == 'unwhitelist':
                try:
                    user_id = int(args[2])
                    if user_id in self.whitelist:
                        self.whitelist.remove(user_id)
                        whitelist_str = ','.join(str(x) for x in self.whitelist
                            )
                        self.config.set('AntiSpam', 'whitelist', whitelist_str)
                        with open(self.config_path, 'w', encoding='utf-8'
                            ) as f:
                            self.config.write(f)
                        await event.edit(
                            f"""**🛡 AntiSpam**

✅ Пользователь `{user_id}` убран из белого списка"""
                            )
                    else:
                        await event.edit(
                            f"""**🛡 AntiSpam**

⚠️ Пользователь `{user_id}` не в белом списке"""
                            )
                except ValueError:
                    await event.edit(
                        f'**🛡 AntiSpam**\n\n❌ Неверный ID пользователя')
            else:
                help_text = f'**🛡 AntiSpam - Помощь**\n\n'
                help_text += f'`{self.prefix}antispam` - включить/выключить\n'
                help_text += (
                    f'`{self.prefix}antispam status` - показать статус\n')
                help_text += (
                    f'`{self.prefix}antispam whitelist <ID>` - добавить в белый список\n'
                    )
                help_text += (
                    f'`{self.prefix}antispam unwhitelist <ID>` - убрать из белого списка'
                    )
                await event.edit(help_text)

        async def incoming_message_handler(event):
            if not self.enabled:
                return
            if event.is_group or event.is_channel:
                return
            sender = await event.get_sender()
            if not sender:
                return
            user_id = sender.id
            me = await self.client.get_me()
            if user_id == me.id:
                return
            if user_id in self.whitelist:
                return
            if user_id in self.blocked_users:
                return
            current_time = time.time()
            self.message_history[user_id].append(current_time)
            self.message_history[user_id] = [t for t in self.
                message_history[user_id] if current_time - t <= self.
                time_window]
            message_count = len(self.message_history[user_id])
            if message_count >= self.max_messages:
                try:
                    from telethon.tl import functions
                    await self.client(functions.contacts.BlockRequest(id=
                        user_id))
                    self.blocked_users.add(user_id)
                    self.total_blocked += 1
                    user_name = sender.first_name or 'Пользователь'
                    username = (f'@{sender.username}' if sender.username else
                        f'ID: {user_id}')
                    notification = f'**🛡 AntiSpam - Блокировка**\n\n'
                    notification += f'❌ Заблокирован спамер:\n'
                    notification += f'👤 {user_name}\n'
                    notification += f'🆔 {username}\n'
                    notification += (
                        f'📊 Отправил {message_count} сообщений за {self.time_window} сек'
                        )
                    await self.client.send_message('me', notification)
                    del self.message_history[user_id]
                except Exception as e:
                    await self.client.send_message('me',
                        f"""**🛡 AntiSpam**

⚠️ Не удалось заблокировать {user_id}: {str(e)}"""
                        )
        client.add_event_handler(antispam_command_handler, events.
            NewMessage(outgoing=True))
        client.add_event_handler(incoming_message_handler, events.
            NewMessage(incoming=True))
