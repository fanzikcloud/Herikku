from core.base_module import Module
import json
import re


class AutoReplyModule(Module):
    NAME = 'AutoReply'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Автоматические ответы на определенные слова в чатах'
    DEPENDENCIES = []
    COMMANDS = {'ar add <триггер> | <ответ>': 'Добавить автоответ',
        'ar list': 'Список всех автоответов', 'ar del <триггер>':
        'Удалить автоответ', 'ar on': 'Включить автоответчик', 'ar off':
        'Выключить автоответчик', 'ar status': 'Статус автоответчика',
        'ar clear': 'Очистить все автоответы'}
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
            text += (
                '• <code>.ar add &lt;слово&gt; | &lt;ответ&gt;</code> - добавить\n'
                )
            text += '• <code>.ar list</code> - список всех\n'
            text += '• <code>.ar del &lt;слово&gt;</code> - удалить\n'
            text += '• <code>.ar on/off</code> - вкл/выкл\n\n'
            if replies:
                text += '<b>Примеры автоответов:</b>\n'
                count = 0
                for trigger, response in list(replies.items())[:3]:
                    text += f'• <code>{trigger}</code> → {response[:30]}...\n'
                    count += 1
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
            for i, (trigger, response) in enumerate(replies.items(), 1):
                message += f'{i}. <b><code>{trigger}</code></b>\n'
                message += (
                    f"   → <i>{response[:50]}{'...' if len(response) > 50 else ''}</i>\n\n"
                    )
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
            text_lower = event.text.lower()
            for trigger, response in replies.items():
                pattern = '\\b' + re.escape(trigger) + '\\b'
                if re.search(pattern, text_lower):
                    try:
                        await event.reply(response)
                        break
                    except Exception as e:
                        print(f'AutoReply error: {e}')
        client.add_event_handler(ar_add_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(ar_list_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(ar_del_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(ar_on_handler, events.NewMessage(outgoing=
            True))
        client.add_event_handler(ar_off_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(ar_status_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(ar_clear_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(incoming_handler, events.NewMessage(
            incoming=True))

    def _get_replies(self):
        replies_json = self.config.get('AutoReply', 'replies', fallback='{}')
        return json.loads(replies_json)

    def _set_replies(self, replies):
        self.config.set('AutoReply', 'replies', json.dumps(replies,
            ensure_ascii=False))
        self._save_config()

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
