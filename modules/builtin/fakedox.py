from core.base_module import Module
import asyncio


class FakeDoxModule(Module):
    NAME = 'FakeDox'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Шуточный модуль деанонимизации (fakedox) с анимацией прогресс-бара'
    DEPENDENCIES = []
    COMMANDS = {
        'dox': 'Шуточный деанон пользователя (в группах нужен реплай, в ЛС работает автоматически)'
    }
    CONFIG_ICON = '🕵️‍♂️'

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def dox_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}dox'):
                return

            target_name = None

            # Если мы в личной переписке (ЛС)
            if event.is_private:
                try:
                    chat_entity = await event.get_chat()
                    target_name = chat_entity.first_name or "Пользователь"
                except Exception:
                    target_name = "Пользователь"
            else:
                # Если мы в группе, супергруппе или канале — проверяем реплай
                if not event.is_reply:
                    await event.edit("<b>❌ В группах необходимо ответить (сделать реплай) на сообщение цели!</b>")
                    return
                try:
                    reply_msg = await event.get_reply_message()
                    sender = await reply_msg.get_sender()
                    if sender:
                        target_name = sender.first_name or "Пользователь"
                    else:
                        target_name = "Пользователь"
                except Exception:
                    target_name = "Пользователь"

            # 1. Этап анимации прогресс-бара
            stages = [
                (0, 35, f"🔍 Ищу информацию про {target_name}...\n"),
                (35, 75, "⏳ Почти у цели...\n"),
                (75, 100, "⏳ Ещё чуть-чуть...\n")
            ]
            
            width = 15
            for start, end, prefix_text in stages:
                step = 5 if (end - start) <= 30 else 10
                for pct in range(start, end + 1, step):
                    filled = int(round(width * (pct / 100)))
                    bar = '█' * filled + '░' * (width - filled)
                    await event.edit(f"{prefix_text}<code>[{bar}] {pct}%</code>")
                    await asyncio.sleep(0.35)
            
            await event.edit("✅ <b>Всё!</b>\n<code>[███████████████] 100%</code>")
            await asyncio.sleep(1.0)

            # 2. Финальный вывод фальшивого докса
            dox_text = (
                "• IP-адрес: сам знаешь\n"
                "• Провайдер: сам знаешь\n"
                "• Страна/город: сам знаешь\n"
                "• Координаты: сам знаешь\n"
                "• Улица и дом: сам знаешь\n"
                "• Номер квартиры: сам знаешь\n"
                "• Операционная система: сам знаешь\n"
                "• Имя: сам знаешь\n"
                "• Местонахождение: сам знаешь\n"
                "• Родители: сам знаешь\n"
                "• Планета: Земля"
            )
            await event.edit(dox_text)

        client.add_event_handler(dox_handler, events.NewMessage(outgoing=True))
