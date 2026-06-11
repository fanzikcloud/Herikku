from core.base_module import Module
import json
import re
import random
import asyncio


class AutoReplyModule(Module):
    NAME = 'AutoReply'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Автоматические ответы на определенные слова в чатах с гибкой кастомизацией'
    DEPENDENCIES = []
    COMMANDS = {
        'ar add <триггер> | <ответ>': 'Добавить простой автоответ',
        'ar addadv <триггер> | <ответы через ;> | [задержка] | [чаты] | [искл. чаты] | [read/noread]': 'Добавить продвинутый автоответ',
        'ar list': 'Список всех автоответов',
        'ar del <триггер>': 'Удалить автоответ',
        'ar on': 'Включить автоответчик',
        'ar off': 'Выключить автоответчик',
        'ar status': 'Статус автоответчика',
        'ar clear': 'Очистить все автоответы'
    }
    CONFIG_ICON = '🤖'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_autoreply':
            enabled = config.get('AutoReply', 'enabled', fallback='no')
            replies_data = config.get('AutoReply', 'replies', fallback='{}')
            replies = json.loads(replies_data)
            text = '<b>🤖 AutoReply - Настройки</b>\n\n'
            text += (
                f"📊 Статус: {'✅ Включен' if enabled == 'yes' else '❌ Выключен'}\n"
                )
            text += f'📝 Автоответов: <b>{len(replies)}</b>\n\n'
            text += '<b>Команды для настройки:</b>\n'
            text += '• <code>.ar add &lt;слово&gt; | &lt;ответ&gt;</code> - простой\n'
            text += '• <code>.ar addadv &lt;триггер&gt; | &lt;ответычерез;&gt; | &lt;задержка&gt; | &lt;чаты&gt; | &lt;исключенные&gt; | &lt;read/noread&gt;</code> - продвинутый\n'
            text += '• <code>.ar list</code> - список всех\n'
            text += '• <code>.ar del &lt;слово&gt;</code> - удалить\n'
            text += '• <code>.ar on/off</code> - вкл/выкл\n\n'
            if replies:
                text += '<b>Примеры автоответов:</b>\n'
                for trigger, val in list(replies.items())[:3]:
                    if isinstance(val, dict):
                        resp_str = "; ".join(val.get('response', []))
                        text += f'• <code>{trigger}</code> (Adv) → {resp_str[:30]}...\n'
                    else:
                        text += f'• <code>{trigger}</code> → {val[:30]}...\n'
                if len(replies) > 3:
                    text += f'<i>...и еще {len(replies) - 3}</i>\n'
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
        if not self.config.has_section('AutoReply'):
            self.config.add_section('AutoReply')
            self.config.set('AutoReply', 'enabled', 'no')
            self.config.set('AutoReply', 'replies', json.dumps({}))
            self._save_config()

        async def ar_add_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar add '):
                return
            args = event.text[len(f'{self.prefix}ar add '):].strip()
            if '|' not in args:
                await event.edit(
                    f"""<b>❌ Неверный формат!</b>

Использование:
<code>{self.prefix}ar add триггер | ответ</code>

Пример:
<code>{self.prefix}ar add привет | Привет! Как дела?</code>"""
                    )
                return
            trigger, response = args.split('|', 1)
            trigger = trigger.strip().lower()
            response = response.strip()
            if not trigger or not response:
                await event.edit(
                    '<b>❌ Триггер и ответ не могут быть пустыми!</b>')
                return
            replies = self._get_replies()
            replies[trigger] = response
            self._set_replies(replies)
            await event.edit(
                f"""<b>✅ Автоответ добавлен!</b>

Триггер: <code>{trigger}</code>
Ответ: <i>{response}</i>"""
                )

        async def ar_addadv_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar addadv '):
                return
            args = event.text[len(f'{self.prefix}ar addadv '):].strip()
            # Формат: триггер | ответ1; ответ2 | задержка | чаты | искл_чаты | read/noread
            parts = [p.strip() for p in args.split('|')]
            if len(parts) < 2:
                await event.edit(
                    f"""<b>❌ Неверный формат!</b>

Использование:
<code>{self.prefix}ar addadv триггер | ответы (через ;) | [задержка] | [чаты] | [искл. чаты] | [read/noread]</code>

Пример:
<code>{self.prefix}ar addadv привет | Привет!; Хей!; Хай | 3 | private, @my_group | spam_chat | read</code>"""
                    )
                return
                
            trigger = parts[0].lower()
            responses = [r.strip() for p in parts[1].split(';') if (r := p.strip())]
            
            if not trigger or not responses:
                await event.edit('<b>❌ Триггер и ответы не могут быть пустыми!</b>')
                return
                
            delay = 0.0
            if len(parts) > 2 and parts[2]:
                try:
                    delay = float(parts[2])
                except ValueError:
                    pass
                    
            allowed_chats = []
            if len(parts) > 3 and parts[3]:
                allowed_chats = [c.strip() for c in parts[3].split(',') if c.strip()]
                
            excluded_chats = []
            if len(parts) > 4 and parts[4]:
                excluded_chats = [c.strip() for c in parts[4].split(',') if c.strip()]
                
            mark_read = False
            if len(parts) > 5 and parts[5].lower() == 'read':
                mark_read = True
                
            replies = self._get_replies()
            replies[trigger] = {
                'response': responses,
                'delay': delay,
                'chats': allowed_chats,
                'exclude_chats': excluded_chats,
                'read': mark_read
            }
            self._set_replies(replies)
            
            chats_str = ", ".join(allowed_chats) if allowed_chats else "везде"
            ex_chats_str = ", ".join(excluded_chats) if excluded_chats else "нет"
            responses_list = "\n".join(f" • {r}" for r in responses)
            await event.edit(
                f"""<b>✅ Продвинутый автоответ добавлен!</b>

🗝 **Триггер**: <code>{trigger}</code>
💬 **Варианты ответов ({len(responses)})**:
<i>{responses_list}</i>
⏱ **Задержка**: <code>{delay} сек</code>
🌐 **Разрешенные чаты**: <code>{chats_str}</code>
🚫 **Исключенные чаты**: <code>{ex_chats_str}</code>
📖 **Читать сообщение**: <code>{"Да" if mark_read else "Нет"}</code>"""
                )

        async def ar_list_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar list'):
                return
            replies = self._get_replies()
            if not replies:
                await event.edit(
                    f"""<b>📝 Список автоответов пуст</b>

Добавьте автоответ командой:
<code>{self.prefix}ar add триггер | ответ</code>"""
                    )
                return
            message = '<b>📝 Список автоответов:</b>\n\n'
            for i, (trigger, val) in enumerate(replies.items(), 1):
                if isinstance(val, dict):
                    responses = val.get('response', [])
                    resp_str = "; ".join(responses)
                    delay = val.get('delay', 0)
                    chats = val.get('chats', [])
                    chats_str = f" [Чаты: {', '.join(chats)}]" if chats else ""
                    delay_str = f" [Пауза: {delay}с]" if delay else ""
                    read_str = " [Чтение: да]" if val.get('read') else ""
                    message += f'{i}. <b><code>{trigger}</code></b> (Adv){chats_str}{delay_str}{read_str}\n'
                    message += f"   → <i>{resp_str[:50]}{'...' if len(resp_str) > 50 else ''}</i>\n\n"
                else:
                    message += f'{i}. <b><code>{trigger}</code></b>\n'
                    message += f"   → <i>{val[:50]}{'...' if len(val) > 50 else ''}</i>\n\n"
            message += f'<b>Всего:</b> {len(replies)}'
            await event.edit(message)

        async def ar_del_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar del '):
                return
            trigger = event.text[len(f'{self.prefix}ar del '):].strip().lower()
            if not trigger:
                await event.edit(
                    f"""<b>❌ Укажите триггер!</b>

Использование:
<code>{self.prefix}ar del триггер</code>"""
                    )
                return
            replies = self._get_replies()
            if trigger in replies:
                del replies[trigger]
                self._set_replies(replies)
                await event.edit(
                    f'<b>✅ Автоответ "<code>{trigger}</code>" удален!</b>')
            else:
                await event.edit(
                    f'<b>❌ Автоответ "<code>{trigger}</code>" не найден!</b>')

        async def ar_on_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar on'):
                return
            self.config.set('AutoReply', 'enabled', 'yes')
            self._save_config()
            replies_count = len(self._get_replies())
            await event.edit(
                f"""<b>✅ Автоответчик включен!</b>

Активных автоответов: <b>{replies_count}</b>"""
                )

        async def ar_off_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar off'):
                return
            self.config.set('AutoReply', 'enabled', 'no')
            self._save_config()
            await event.edit('<b>❌ Автоответчик выключен!</b>')

        async def ar_status_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar status'):
                return
            enabled = self.config.get('AutoReply', 'enabled', fallback='no')
            replies = self._get_replies()
            status_emoji = '✅' if enabled == 'yes' else '❌'
            status_text = 'Включен' if enabled == 'yes' else 'Выключен'
            message = '<b>🤖 AutoReply - Статус</b>\n\n'
            message += f'{status_emoji} Статус: <b>{status_text}</b>\n'
            message += f'📝 Автоответов: <b>{len(replies)}</b>\n\n'
            if replies:
                message += '<b>Последние добавленные:</b>\n'
                for trigger in list(replies.keys())[-5:]:
                    message += f'• <code>{trigger}</code>\n'
            await event.edit(message)

        async def ar_clear_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}ar clear'):
                return
            replies = self._get_replies()
            count = len(replies)
            self._set_replies({})
            await event.edit(
                f'<b>🗑 Все автоответы удалены!</b>\n\nУдалено: <b>{count}</b>')

        async def incoming_handler(event):
            enabled = self.config.get('AutoReply', 'enabled', fallback='no')
            if enabled != 'yes':
                return
            if not event.text:
                return
            replies = self._get_replies()
            if not replies:
                return
                
            chat_id = event.chat_id
            chat_entity = None
            chat_username = None
            try:
                chat_entity = await event.get_chat()
                if hasattr(chat_entity, 'username') and chat_entity.username:
                    chat_username = chat_entity.username.lower()
            except:
                pass

            text_lower = event.text.lower()
            for trigger, data in replies.items():
                pattern = '\\b' + re.escape(trigger) + '\\b'
                if re.search(pattern, text_lower):
                    responses = []
                    delay = 0.0
                    mark_read = False
                    allowed_chats = []
                    excluded_chats = []

                    if isinstance(data, dict):
                        resp_val = data.get('response', '')
                        if isinstance(resp_val, list):
                            responses = resp_val
                        else:
                            responses = [resp_val] if resp_val else []
                        
                        delay = float(data.get('delay', 0.0))
                        mark_read = bool(data.get('read', False))
                        allowed_chats = data.get('chats', [])
                        excluded_chats = data.get('exclude_chats', [])
                    else:
                        responses = [data]

                    # 1. Проверка на исключенные чаты
                    is_excluded = False
                    for ex in excluded_chats:
                        ex_str = str(ex).strip().lower()
                        if ex_str.startswith('@'):
                            ex_str = ex_str[1:]
                        if str(chat_id) == ex_str or (chat_username and chat_username == ex_str):
                            is_excluded = True
                            break
                    if is_excluded:
                        continue

                    # 2. Проверка на разрешенные чаты
                    if allowed_chats:
                        is_allowed = False
                        for ch in allowed_chats:
                            ch_str = str(ch).strip().lower()
                            if ch_str.startswith('@'):
                                ch_str = ch_str[1:]
                            
                            # Проверка по ID или юзернейму
                            if str(chat_id) == ch_str or (chat_username and chat_username == ch_str):
                                is_allowed = True
                                break
                            
                            # Проверка по типу чата
                            if ch_str == 'private' and event.is_private:
                                is_allowed = True
                                break
                            elif ch_str == 'group' and (event.is_group or event.is_channel):
                                is_allowed = True
                                break
                        if not is_allowed:
                            continue

                    if not responses:
                        continue

                    response_text = random.choice(responses)

                    try:
                        # Опция "Прочитать сообщение сначала"
                        if mark_read:
                            await event.mark_read()
                        
                        # Задержка перед ответом
                        if delay > 0.0:
                            await asyncio.sleep(delay)
                            
                        await event.reply(response_text)
                        break
                    except Exception as e:
                        print(f'AutoReply error: {e}')

        client.add_event_handler(ar_add_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ar_addadv_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ar_list_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ar_del_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ar_on_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ar_off_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ar_status_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ar_clear_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(incoming_handler, events.NewMessage(incoming=True))

    def _get_replies(self):
        replies_json = self.config.get('AutoReply', 'replies', fallback='{}')
        return json.loads(replies_json)

    def _set_replies(self, replies):
        self.config.set('AutoReply', 'replies', json.dumps(replies, ensure_ascii=False))
        self._save_config()

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
