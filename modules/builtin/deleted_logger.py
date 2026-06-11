from core.base_module import Module
from datetime import datetime
import io


class DeletedLoggerModule(Module):
    NAME = 'DeletedLogger'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Логирование удалённых сообщений в inline-бота'
    DEPENDENCIES = []
    COMMANDS = {
        'dlog': 'Включить/выключить логирование удалённых сообщений',
        'dlog status': 'Показать статус логирования',
        'dlog blacklist <ID>': 'Добавить чат в чёрный список',
        'dlog unblacklist <ID>': 'Убрать чат из чёрного списка',
        'dlog whitelist': 'Показать белый список (логируются только эти чаты)',
        'dlog addwhite <ID>': 'Добавить чат в белый список',
        'dlog remwhite <ID>': 'Убрать чат из белого списка',
    }
    CONFIG_ICON = '🗑️'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_deleted_logger':
            enabled = config.getboolean('DeletedLogger', 'enabled', fallback=False)
            mode = config.get('DeletedLogger', 'mode', fallback='all')
            blacklist = config.get('DeletedLogger', 'blacklist', fallback='')
            whitelist = config.get('DeletedLogger', 'whitelist', fallback='')
            
            blacklist_count = len([x for x in blacklist.split(',') if x.strip()])
            whitelist_count = len([x for x in whitelist.split(',') if x.strip()])
            
            text = '<b>🗑️ DeletedLogger - Настройки</b>\n\n'
            text += f'📊 <b>Статус:</b> {"✅ Включен" if enabled else "❌ Выключен"}\n'
            text += f'🎯 <b>Режим:</b> {mode}\n'
            text += f'🚫 <b>Чёрный список:</b> {blacklist_count} чатов\n'
            text += f'✅ <b>Белый список:</b> {whitelist_count} чатов\n\n'
            
            text += '<b>Режимы работы:</b>\n'
            text += '• <code>all</code> - все чаты кроме чёрного списка\n'
            text += '• <code>whitelist</code> - только чаты из белого списка\n\n'
            
            text += '<b>Команды:</b>\n'
            text += '• <code>.dlog</code> - вкл/выкл\n'
            text += '• <code>.dlog status</code> - статус\n'
            text += '• <code>.dlog blacklist &lt;ID&gt;</code> - в чёрный список\n'
            text += '• <code>.dlog addwhite &lt;ID&gt;</code> - в белый список\n'
            
            buttons = [[Button.inline('◀️ К модулям', b'menu_modules')]]
            await event.edit(text, buttons=buttons)
        else:
            raise Exception('Not our callback')

    async def init(self, client, command_prefix, events, load_module,
                   loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.config_path = config_path
        self.bot_start_time = bot_start_time

        me = await client.get_me()
        self.owner_id = me.id

        if not config.has_section('DeletedLogger'):
            config.add_section('DeletedLogger')
            config.set('DeletedLogger', 'enabled', 'False')
            config.set('DeletedLogger', 'mode', 'all')
            config.set('DeletedLogger', 'blacklist', '')
            config.set('DeletedLogger', 'whitelist', '')
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)

        self.enabled = config.getboolean('DeletedLogger', 'enabled', fallback=False)
        self.mode = config.get('DeletedLogger', 'mode', fallback='all')

        blacklist_str = config.get('DeletedLogger', 'blacklist', fallback='')
        self.blacklist = set(int(x.strip()) for x in blacklist_str.split(',') if x.strip())

        whitelist_str = config.get('DeletedLogger', 'whitelist', fallback='')
        self.whitelist = set(int(x.strip()) for x in whitelist_str.split(',') if x.strip())

        self.message_cache = {}

        self.inline_bot_username = config.get('InlineBot', 'username', fallback='')

        await self.setup_handlers(client, events)

    def _should_log_chat(self, chat_id: int) -> bool:
        """Проверяет нужно ли логировать этот чат."""
        if self.mode == 'whitelist':
            return chat_id in self.whitelist
        else:  # mode == 'all'
            return chat_id not in self.blacklist

    async def _log_once_media(self, event):
        """Логирует единоразовые медиа (кружочки, фото/видео с ttl)."""
        if not self.inline_bot_username:
            return
        
        try:
            chat_id = event.chat_id
            chat = await self.client.get_entity(chat_id)
            chat_title = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Unknown')
            
            try:
                sender = await self.client.get_entity(event.sender_id)
                sender_name = getattr(sender, 'first_name', 'Unknown')
                sender_username = f"@{sender.username}" if getattr(sender, 'username', None) else f"ID: {event.sender_id}"
            except:
                sender_name = 'Unknown'
                sender_username = f"ID: {event.sender_id}"
            
            log_text = f'👁️ <b>Единоразовое медиа</b>\n\n'
            log_text += f'📍 <b>Чат:</b> {chat_title}\n'
            log_text += f'🆔 <b>Chat ID:</b> <code>{chat_id}</code>\n'
            log_text += f'👤 <b>От:</b> {sender_name} ({sender_username})\n'
            log_text += f'🕐 <b>Время:</b> {event.date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
            
            if event.text:
                log_text += f'💬 <b>Подпись:</b>\n{event.text[:300]}'
                if len(event.text) > 300:
                    log_text += '...'

            from main import account_bots
            if self.owner_id in account_bots:
                bot_client = account_bots[self.owner_id]
                try:
                    await bot_client.send_message(
                        self.owner_id,
                        log_text,
                        file=event.media
                    )
                except Exception as e:
                    log_text += f'\n\n⚠️ <i>Не удалось загрузить медиа: {str(e)}</i>'
                    await bot_client.send_message(self.owner_id, log_text)
        except Exception as e:
            pass

    async def _send_log_to_owner(self, log_text: str, media=None):
        try:
            from main import account_bots
            if self.owner_id in account_bots:
                bot_client = account_bots[self.owner_id]
                if media:
                    await bot_client.send_message(self.owner_id, log_text, file=media)
                else:
                    await bot_client.send_message(self.owner_id, log_text)
        except Exception as e:
            await self.client.send_message('me', log_text)

    async def setup_handlers(self, client, events):

        async def dlog_command_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}dlog'):
                return

            args = event.text.split()

            if len(args) == 1:
                self.enabled = not self.enabled
                self.config.set('DeletedLogger', 'enabled', str(self.enabled))
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                
                status = '✅ Включен' if self.enabled else '❌ Выключен'
                await event.edit(
                    f'**🗑️ DeletedLogger**\n\n'
                    f'{status}\n\n'
                    f'Удалённые сообщения будут отправляться в @{self.inline_bot_username}'
                )
            
            elif len(args) == 2 and args[1].lower() == 'status':
                status = '✅ Включен' if self.enabled else '❌ Выключен'
                message = f'**🗑️ DeletedLogger - Статус**\n\n'
                message += f'Состояние: {status}\n'
                message += f'Режим: {self.mode}\n'
                message += f'Чёрный список: {len(self.blacklist)} чатов\n'
                message += f'Белый список: {len(self.whitelist)} чатов\n'
                message += f'Inline-бот: @{self.inline_bot_username}\n'
                await event.edit(message)
            
            elif len(args) == 3 and args[1].lower() == 'blacklist':
                try:
                    chat_id = int(args[2])
                    self.blacklist.add(chat_id)
                    blacklist_str = ','.join(str(x) for x in self.blacklist)
                    self.config.set('DeletedLogger', 'blacklist', blacklist_str)
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        self.config.write(f)
                    await event.edit(f'**🗑️ DeletedLogger**\n\n✅ Чат `{chat_id}` добавлен в чёрный список')
                except ValueError:
                    await event.edit('**🗑️ DeletedLogger**\n\n❌ Неверный ID чата')
            
            elif len(args) == 3 and args[1].lower() == 'unblacklist':
                try:
                    chat_id = int(args[2])
                    if chat_id in self.blacklist:
                        self.blacklist.remove(chat_id)
                        blacklist_str = ','.join(str(x) for x in self.blacklist)
                        self.config.set('DeletedLogger', 'blacklist', blacklist_str)
                        with open(self.config_path, 'w', encoding='utf-8') as f:
                            self.config.write(f)
                        await event.edit(f'**🗑️ DeletedLogger**\n\n✅ Чат `{chat_id}` убран из чёрного списка')
                    else:
                        await event.edit(f'**🗑️ DeletedLogger**\n\n⚠️ Чат `{chat_id}` не в чёрном списке')
                except ValueError:
                    await event.edit('**🗑️ DeletedLogger**\n\n❌ Неверный ID чата')
            
            elif len(args) == 2 and args[1].lower() == 'whitelist':
                if self.whitelist:
                    message = '**🗑️ DeletedLogger - Белый список**\n\n'
                    for chat_id in list(self.whitelist)[:20]:
                        message += f'• `{chat_id}`\n'
                    if len(self.whitelist) > 20:
                        message += f'• ... и ещё {len(self.whitelist) - 20}\n'
                else:
                    message = '**🗑️ DeletedLogger**\n\n⚠️ Белый список пуст'
                await event.edit(message)
            
            elif len(args) == 3 and args[1].lower() == 'addwhite':
                try:
                    chat_id = int(args[2])
                    self.whitelist.add(chat_id)
                    whitelist_str = ','.join(str(x) for x in self.whitelist)
                    self.config.set('DeletedLogger', 'whitelist', whitelist_str)
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        self.config.write(f)
                    await event.edit(f'**🗑️ DeletedLogger**\n\n✅ Чат `{chat_id}` добавлен в белый список')
                except ValueError:
                    await event.edit('**🗑️ DeletedLogger**\n\n❌ Неверный ID чата')
            
            elif len(args) == 3 and args[1].lower() == 'remwhite':
                try:
                    chat_id = int(args[2])
                    if chat_id in self.whitelist:
                        self.whitelist.remove(chat_id)
                        whitelist_str = ','.join(str(x) for x in self.whitelist)
                        self.config.set('DeletedLogger', 'whitelist', whitelist_str)
                        with open(self.config_path, 'w', encoding='utf-8') as f:
                            self.config.write(f)
                        await event.edit(f'**🗑️ DeletedLogger**\n\n✅ Чат `{chat_id}` убран из белого списка')
                    else:
                        await event.edit(f'**🗑️ DeletedLogger**\n\n⚠️ Чат `{chat_id}` не в белом списке')
                except ValueError:
                    await event.edit('**🗑️ DeletedLogger**\n\n❌ Неверный ID чата')
            
            else:
                help_text = f'**🗑️ DeletedLogger - Помощь**\n\n'
                help_text += f'`{self.prefix}dlog` - включить/выключить\n'
                help_text += f'`{self.prefix}dlog status` - показать статус\n'
                help_text += f'`{self.prefix}dlog blacklist <ID>` - в чёрный список\n'
                help_text += f'`{self.prefix}dlog unblacklist <ID>` - из чёрного списка\n'
                help_text += f'`{self.prefix}dlog whitelist` - показать белый список\n'
                help_text += f'`{self.prefix}dlog addwhite <ID>` - в белый список\n'
                help_text += f'`{self.prefix}dlog remwhite <ID>` - из белого списка'
                await event.edit(help_text)

        async def message_handler(event):
            if not self.enabled:
                return

            chat_id = event.chat_id
            if not self._should_log_chat(chat_id):
                return

            is_once_media = False
            if event.media and hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
                is_once_media = True

            self.message_cache[event.id] = {
                'chat_id': chat_id,
                'sender_id': event.sender_id,
                'text': event.text or '',
                'date': event.date,
                'media': event.media,
                'message': event.message,
                'is_once': is_once_media,
            }

            if is_once_media:
                await self._log_once_media(event)

        async def deleted_handler(event):
            if not self.enabled:
                return

            if not self.inline_bot_username:
                return

            for msg_id in event.deleted_ids:
                if msg_id not in self.message_cache:
                    continue
                
                cached = self.message_cache[msg_id]
                chat_id = cached['chat_id']
                
                if not self._should_log_chat(chat_id):
                    del self.message_cache[msg_id]
                    continue

                try:
                    chat = await self.client.get_entity(chat_id)
                    chat_title = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Unknown')

                    try:
                        sender = await self.client.get_entity(cached['sender_id'])
                        sender_name = getattr(sender, 'first_name', 'Unknown')
                        sender_username = f"@{sender.username}" if getattr(sender, 'username', None) else f"ID: {cached['sender_id']}"
                    except:
                        sender_name = 'Unknown'
                        sender_username = f"ID: {cached['sender_id']}"

                    log_text = f'🗑️ <b>Удалённое сообщение</b>\n\n'
                    log_text += f'📍 <b>Чат:</b> {chat_title}\n'
                    log_text += f'🆔 <b>Chat ID:</b> <code>{chat_id}</code>\n'
                    log_text += f'👤 <b>От:</b> {sender_name} ({sender_username})\n'
                    log_text += f'🕐 <b>Время:</b> {cached["date"].strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                    
                    if cached['text']:
                        log_text += f'💬 <b>Текст:</b>\n{cached["text"][:500]}'
                        if len(cached['text']) > 500:
                            log_text += '...'

                    if cached['media'] and not cached.get('is_once'):
                        try:
                            await self._send_log_to_owner(log_text, cached['message'].media)
                        except:
                            log_text += '\n\n📎 <i>Медиа-файл (не удалось загрузить)</i>'
                            await self._send_log_to_owner(log_text)
                    else:
                        await self._send_log_to_owner(log_text)
                    
                except Exception as e:
                    # Если произошла ошибка, отправляем базовую информацию
                    error_text = f'�️ <b>Удалённое сообщение</b>\n\n'
                    error_text += f'🆔 <b>Chat ID:</b> <code>{chat_id}</code>\n'
                    error_text += f'📝 <b>Message ID:</b> <code>{msg_id}</code>\n'
                    if cached.get('text'):
                        error_text += f'💬 <b>Текст:</b>\n{cached["text"][:300]}'
                        if len(cached['text']) > 300:
                            error_text += '...'
                        error_text += '\n\n'
                    error_text += f'⚠️ <i>Ошибка получения деталей: {str(e)}</i>'
                    await self._send_log_to_owner(error_text)

                del self.message_cache[msg_id]
        
        client.add_event_handler(dlog_command_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(message_handler, events.NewMessage(incoming=True))
        client.add_event_handler(deleted_handler, events.MessageDeleted())
