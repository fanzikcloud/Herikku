from core.base_module import Module
import asyncio


class SpamModule(Module):
    NAME = 'Spam'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Модуль для отправки повторяющихся сообщений'
    DEPENDENCIES = []
    COMMANDS = {'spam':
        'Спам сообщениями (.spam <кол-во> <текст> <задержка>)', 'stopspam':
        'Остановить все активные спамы', 'spams':
        'Отправить слова по отдельности (.spams <текст>)'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.spam_tasks = {}

        async def spam_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}spam'
                ):
                return
            parts = event.text.split(maxsplit=3)
            if len(parts) < 3:
                await event.edit(
                    f"""**📨 Использование:**
`{self.prefix}spam <количество> <текст> [задержка]`

**Примеры:**
• `{self.prefix}spam 10 Привет` - 10 раз
• `{self.prefix}spam 0 Привет` - бесконечно
• `{self.prefix}spam 5 Привет 2` - 5 раз с задержкой 2 сек"""
                    )
                return
            try:
                count = int(parts[1])
                if count < 0:
                    await event.edit('❌ Количество не может быть отрицательным'
                        )
                    return
            except ValueError:
                await event.edit('❌ Количество должно быть числом')
                return
            remaining = parts[2] if len(parts) == 3 else ' '.join(parts[2:])
            text_parts = remaining.rsplit(maxsplit=1)
            delay = 0
            if len(text_parts) == 2 and text_parts[1].replace('.', '', 1
                ).isdigit():
                message_text = text_parts[0]
                try:
                    delay = float(text_parts[1])
                except ValueError:
                    message_text = remaining
                    delay = 0
            else:
                message_text = remaining
                delay = 0
            chat_id = event.chat_id
            if chat_id in self.spam_tasks:
                self.spam_tasks[chat_id].cancel()
            await event.delete()

            async def spam_task():
                try:
                    sent = 0
                    infinite = count == 0
                    while infinite or sent < count:
                        await self.client.send_message(chat_id, message_text)
                        sent += 1
                        if delay > 0:
                            await asyncio.sleep(delay)
                        else:
                            await asyncio.sleep(0.1)
                    if chat_id in self.spam_tasks:
                        del self.spam_tasks[chat_id]
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f'Ошибка спама: {e}')
            task = asyncio.create_task(spam_task())
            self.spam_tasks[chat_id] = task
            if count == 0:
                notification = await self.client.send_message(chat_id,
                    f"""♾️ Запущен бесконечный спам
⏱ Задержка: {delay if delay > 0 else 0.1} сек"""
                    )
            else:
                notification = await self.client.send_message(chat_id,
                    f"""📨 Запущен спам: {count} сообщений
⏱ Задержка: {delay if delay > 0 else 0.1} сек"""
                    )
            await asyncio.sleep(3)
            await notification.delete()

        async def stopspam_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}stopspam'):
                return
            chat_id = event.chat_id
            if chat_id in self.spam_tasks:
                self.spam_tasks[chat_id].cancel()
                del self.spam_tasks[chat_id]
                await event.edit('✅ Спам остановлен')
            else:
                await event.edit('⚠️ Активных спамов в этом чате нет')
            await asyncio.sleep(2)
            await event.delete()

        async def spams_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}spams'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.edit(
                    f"""**📝 Использование:**
`{self.prefix}spams <текст>`

**Пример:**
`{self.prefix}spams Привет как дела` - отправит 3 сообщения"""
                    )
                return
            message_text = parts[1]
            words = message_text.split()
            if not words:
                await event.edit('❌ Текст не может быть пустым')
                return
            chat_id = event.chat_id
            await event.delete()
            for word in words:
                await self.client.send_message(chat_id, word)
                await asyncio.sleep(0.5)
        client.add_event_handler(spam_handler, events.NewMessage(outgoing=True)
            )
        client.add_event_handler(stopspam_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(spams_handler, events.NewMessage(outgoing=
            True))

    async def dispose(self):
        for task in self.spam_tasks.values():
            task.cancel()
        self.spam_tasks.clear()
