from core.base_module import Module
import asyncio


class ReactModule(Module):
    NAME = 'Reaction Spam'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Ставит реакции на последние N сообщений в чате'
    DEPENDENCIES = []
    COMMANDS = {
        'react': 'Поставить реакцию на последние N сообщений (например: .react ❤️ 10)',
        'unreact': 'Убрать свои реакции с последних N сообщений (например: .unreact 10)',
    }

    async def init(self, client, command_prefix, events, load_module,
                   loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def react_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}react'):
                return
            if event.text.startswith(f'{self.prefix}unreact'):
                return

            parts = event.text.split()
            # .react ❤️ 10  или  .react ❤️  (по умолчанию 10)
            if len(parts) < 2:
                await event.edit(
                    '**💥 Reaction Spam**\n\n'
                    f'❌ Укажи эмодзи!\n'
                    f'Использование: `{self.prefix}react <эмодзи> [кол-во]`\n\n'
                    f'Пример: `{self.prefix}react ❤️ 20`'
                )
                return

            emoji = parts[1]
            count = 10
            if len(parts) >= 3:
                try:
                    count = int(parts[2])
                except ValueError:
                    await event.edit(
                        '**💥 Reaction Spam**\n\n'
                        f'❌ Неверное количество!\n'
                        f'Использование: `{self.prefix}react <эмодзи> [кол-во]`'
                    )
                    return

            if count < 1 or count > 200:
                await event.edit(
                    '**💥 Reaction Spam**\n\n'
                    '❌ Количество должно быть от 1 до 200'
                )
                return

            await event.edit(
                f'**💥 Reaction Spam**\n\n'
                f'⏳ Ставлю {emoji} на последние **{count}** сообщений...'
            )

            from telethon.tl.functions.messages import SendReactionRequest
            from telethon.tl.types import ReactionEmoji

            success = 0
            failed = 0
            processed = 0

            async for msg in client.iter_messages(event.chat_id, limit=count + 1):
                # Пропускаем наше собственное сообщение с командой
                if msg.id == event.id:
                    continue

                processed += 1
                if processed > count:
                    break

                try:
                    await client(SendReactionRequest(
                        peer=event.chat_id,
                        msg_id=msg.id,
                        reaction=[ReactionEmoji(emoticon=emoji)]
                    ))
                    success += 1
                except Exception:
                    failed += 1

                # Обновляем прогресс каждые 10 сообщений
                if processed % 10 == 0:
                    try:
                        await event.edit(
                            f'**💥 Reaction Spam**\n\n'
                            f'⏳ Прогресс: **{processed}/{count}**\n'
                            f'✅ Успешно: **{success}** | ❌ Ошибок: **{failed}**'
                        )
                    except Exception:
                        pass

                await asyncio.sleep(0.3)

            await event.edit(
                f'**💥 Reaction Spam — Готово!**\n\n'
                f'Эмодзи: {emoji}\n'
                f'✅ Поставлено: **{success}** реакций\n'
                f'❌ Ошибок: **{failed}**\n'
                f'📊 Обработано: **{processed}** сообщений'
            )

        async def unreact_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}unreact'):
                return

            parts = event.text.split()
            count = 10
            if len(parts) >= 2:
                try:
                    count = int(parts[1])
                except ValueError:
                    await event.edit(
                        '**💥 Unreact**\n\n'
                        f'❌ Неверное количество!\n'
                        f'Использование: `{self.prefix}unreact [кол-во]`'
                    )
                    return

            if count < 1 or count > 200:
                await event.edit(
                    '**💥 Unreact**\n\n'
                    '❌ Количество должно быть от 1 до 200'
                )
                return

            await event.edit(
                f'**💥 Unreact**\n\n'
                f'⏳ Убираю реакции с последних **{count}** сообщений...'
            )

            from telethon.tl.functions.messages import SendReactionRequest

            success = 0
            failed = 0
            processed = 0

            async for msg in client.iter_messages(event.chat_id, limit=count + 1):
                if msg.id == event.id:
                    continue

                processed += 1
                if processed > count:
                    break

                try:
                    await client(SendReactionRequest(
                        peer=event.chat_id,
                        msg_id=msg.id,
                        reaction=[]
                    ))
                    success += 1
                except Exception:
                    failed += 1

                await asyncio.sleep(0.3)

            await event.edit(
                f'**💥 Unreact — Готово!**\n\n'
                f'✅ Убрано реакций: **{success}**\n'
                f'❌ Ошибок: **{failed}**\n'
                f'📊 Обработано: **{processed}** сообщений'
            )

        client.add_event_handler(react_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(unreact_handler, events.NewMessage(outgoing=True))
