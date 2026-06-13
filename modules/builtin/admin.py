from core.base_module import Module
import asyncio
import re
from datetime import datetime, timedelta
from telethon import events, types, functions
from telethon.errors import UserAdminInvalidError, ChatAdminRequiredError


class AdminModule(Module):
    NAME = 'AdminTools'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Управление собственными чатами (бан, кик, мут, размут, очистка, пин, инфо о пользователе)'
    DEPENDENCIES = []
    COMMANDS = {
        'ban <реплай/@username/ID> [время]': 'Забанить пользователя в чате (навсегда или временно, например 10m, 2h, 1d)',
        'unban <реплай/@username/ID>': 'Разбанить пользователя в чате',
        'kick <реплай/@username/ID>': 'Кикнуть (удалить) пользователя из чата',
        'mute <реплай/@username/ID> [время]': 'Замутить пользователя (запретить писать) навсегда или на время',
        'unmute <реплай/@username/ID>': 'Размутить пользователя',
        'purge': 'Удалить все сообщения от выделенного (реплаем) сообщения до текущего',
        'del': 'Удалить сообщение, на которое сделан реплай',
        'pin': 'Закрепить сообщение из реплая',
        'unpin': 'Открепить сообщение из реплая (или последнее)',
        'user <реплай/@username/ID>': 'Показать детальную информацию о пользователе чата'
    }
    CONFIG_ICON = '🛡️'

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        def parse_time(time_str):
            if not time_str:
                return None
            match = re.match(r'^(\d+)([mhdw])$', time_str.lower())
            if not match:
                return None
            value, unit = match.groups()
            value = int(value)
            if unit == 'm':
                return timedelta(minutes=value)
            elif unit == 'h':
                return timedelta(hours=value)
            elif unit == 'd':
                return timedelta(days=value)
            elif unit == 'w':
                return timedelta(weeks=value)
            return None

        async def get_user_from_event(event, text_after_cmd):
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    user_entity = await self.client.get_entity(reply_msg.sender_id)
                    return user_entity, text_after_cmd

            parts = text_after_cmd.split(maxsplit=1) if text_after_cmd else []
            if not parts:
                return None, ""

            target = parts[0]
            remaining_text = parts[1].strip() if len(parts) > 1 else ""

            try:
                if target.isdigit():
                    user_entity = await self.client.get_entity(int(target))
                elif target.startswith('-') and target[1:].isdigit():
                    user_entity = await self.client.get_entity(int(target))
                else:
                    user_entity = await self.client.get_entity(target)
                return user_entity, remaining_text
            except Exception:
                return None, text_after_cmd

        async def ban_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}ban'):
                return
            
            if event.is_private:
                await event.edit("<b>❌ Команда доступна только в группах и каналах!</b>")
                return

            args = event.text[len(f'{self.prefix}ban'):].strip()
            user, time_arg = await get_user_from_event(event, args)

            if not user:
                await event.edit(
                    f"<b>❌ Укажите пользователя!</b>\n"
                    f"Ответьте на СМС или введите: <code>{self.prefix}ban @username [время]</code>"
                )
                return

            until_date = None
            duration_str = "навсегда"
            if time_arg:
                duration = parse_time(time_arg)
                if duration:
                    until_date = datetime.now() + duration
                    duration_str = f"на {time_arg}"
                else:
                    pass

            await event.edit(f"<b>⏳ Блокировка пользователя {user.first_name}...</b>")

            try:
                await self.client.edit_permissions(
                    entity=event.chat_id,
                    user=user,
                    until_date=until_date,
                    view_messages=False
                )
                await event.edit(
                    f"<b>🚫 Пользователь <a href='tg://user?id={user.id}'>{user.first_name}</a> успешно забанен {duration_str}!</b>"
                )
            except ChatAdminRequiredError:
                await event.edit("<b>❌ Ошибка: У Вас нет прав администратора в этом чате!</b>")
            except UserAdminInvalidError:
                await event.edit("<b>❌ Ошибка: Невозможно забанить администратора или создателя чата!</b>")
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось забанить:</b>\n<code>{str(e)}</code>")

        async def unban_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}unban'):
                return
            if event.is_private:
                await event.edit("<b>❌ Команда доступна только в группах и каналах!</b>")
                return

            args = event.text[len(f'{self.prefix}unban'):].strip()
            user, _ = await get_user_from_event(event, args)

            if not user:
                await event.edit("<b>❌ Укажите пользователя для разбана!</b>")
                return

            await event.edit(f"<b>⏳ Разблокировка пользователя {user.first_name}...</b>")

            try:
                await self.client.edit_permissions(
                    entity=event.chat_id,
                    user=user
                )
                await event.edit(
                    f"<b>✅ Пользователь <a href='tg://user?id={user.id}'>{user.first_name}</a> успешно разбанен!</b>"
                )
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось разбанить:</b>\n<code>{str(e)}</code>")

        async def kick_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}kick'):
                return
            if event.is_private:
                await event.edit("<b>❌ Команда доступна только в группах и каналах!</b>")
                return

            args = event.text[len(f'{self.prefix}kick'):].strip()
            user, _ = await get_user_from_event(event, args)

            if not user:
                await event.edit("<b>❌ Укажите пользователя для кика!</b>")
                return

            await event.edit(f"<b>⏳ Удаление пользователя {user.first_name} из чата...</b>")

            try:
                await self.client.kick_participant(event.chat_id, user)
                await event.edit(
                    f"<b>👢 Пользователь <a href='tg://user?id={user.id}'>{user.first_name}</a> успешно кикнут из чата!</b>"
                )
            except ChatAdminRequiredError:
                await event.edit("<b>❌ Ошибка: Нет прав администратора для кика!</b>")
            except UserAdminInvalidError:
                await event.edit("<b>❌ Ошибка: Невозможно кикнуть администратора!</b>")
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось кикнуть:</b>\n<code>{str(e)}</code>")

        async def mute_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}mute'):
                return
            if event.is_private:
                await event.edit("<b>❌ Команда доступна только в группах и каналах!</b>")
                return

            args = event.text[len(f'{self.prefix}mute'):].strip()
            user, time_arg = await get_user_from_event(event, args)

            if not user:
                await event.edit("<b>❌ Укажите пользователя для мута!</b>")
                return

            until_date = None
            duration_str = "навсегда"
            if time_arg:
                duration = parse_time(time_arg)
                if duration:
                    until_date = datetime.now() + duration
                    duration_str = f"на {time_arg}"

            await event.edit(f"<b>⏳ Ограничение отправки сообщений для {user.first_name}...</b>")

            try:
                await self.client.edit_permissions(
                    entity=event.chat_id,
                    user=user,
                    until_date=until_date,
                    send_messages=False
                )
                await event.edit(
                    f"<b>🔇 Пользователю <a href='tg://user?id={user.id}'>{user.first_name}</a> запрещено писать сообщения {duration_str}!</b>"
                )
            except ChatAdminRequiredError:
                await event.edit("<b>❌ Ошибка: Нет прав администратора для мута!</b>")
            except UserAdminInvalidError:
                await event.edit("<b>❌ Ошибка: Невозможно замутить администратора!</b>")
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось выдать мут:</b>\n<code>{str(e)}</code>")

        async def unmute_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}unmute'):
                return
            if event.is_private:
                await event.edit("<b>❌ Команда доступна только в группах и каналах!</b>")
                return

            args = event.text[len(f'{self.prefix}unmute'):].strip()
            user, _ = await get_user_from_event(event, args)

            if not user:
                await event.edit("<b>❌ Укажите пользователя для размута!</b>")
                return

            await event.edit(f"<b>⏳ Восстановление прав для {user.first_name}...</b>")

            try:

                await self.client.edit_permissions(
                    entity=event.chat_id,
                    user=user,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True
                )
                await event.edit(
                    f"<b>🔊 Пользователь <a href='tg://user?id={user.id}'>{user.first_name}</a> успешно размучен!</b>"
                )
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось размутить:</b>\n<code>{str(e)}</code>")

        async def purge_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}purge'):
                return
            if not event.is_reply:
                await event.edit("<b>❌ Сделайте реплей на СМС, с которого нужно начать очистку!</b>")
                return

            reply_msg = await event.get_reply_message()
            start_id = reply_msg.id
            end_id = event.id

            await event.edit("<b>⏳ Начинаю очистку истории сообщений...</b>")

            messages_to_delete = []
            try:
                async for msg in self.client.iter_messages(event.chat_id, min_id=start_id - 1, max_id=end_id + 1):
                    messages_to_delete.append(msg.id)
                    if len(messages_to_delete) >= 100:
                        await self.client.delete_messages(event.chat_id, messages_to_delete)
                        messages_to_delete = []

                if messages_to_delete:
                    await self.client.delete_messages(event.chat_id, messages_to_delete)

                notification = await self.client.send_message(event.chat_id, "<b>🧹 Очистка чата успешно завершена!</b>")
                await asyncio.sleep(3)
                await notification.delete()
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось очистить историю:</b>\n<code>{str(e)}</code>")

        async def del_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}del'):
                return
            if not event.is_reply:
                await event.edit("<b>❌ Ответьте этой командой на сообщение, которое нужно удалить!</b>")
                return

            reply_msg = await event.get_reply_message()
            try:
                await reply_msg.delete()
                await event.delete()
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось удалить сообщение:</b>\n<code>{str(e)}</code>")

        async def pin_handler(event):
            if not event.text or not event.text.startswith((f'{self.prefix}pin', f'{self.prefix}unpin')):
                return
            if event.is_private:
                await event.edit("<b>❌ Команда доступна только в группах и каналах!</b>")
                return

            is_pin = event.text.startswith(f'{self.prefix}pin')

            if is_pin:
                if not event.is_reply:
                    await event.edit("<b>❌ Ответьте этой командой на сообщение для закрепа!</b>")
                    return
                reply_msg = await event.get_reply_message()
                try:
                    await self.client.pin_message(event.chat_id, reply_msg.id, notify=False)
                    await event.delete()
                except Exception as e:
                    await event.edit(f"<b>❌ Не удалось закрепить сообщение:</b>\n<code>{str(e)}</code>")
            else:
                try:
                    if event.is_reply:
                        reply_msg = await event.get_reply_message()
                        await self.client.unpin_message(event.chat_id, reply_msg.id)
                    else:
                        await self.client(functions.messages.UnpinAllMessagesRequest(peer=event.chat_id))
                    await event.delete()
                except Exception as e:
                    await event.edit(f"<b>❌ Не удалось открепить:</b>\n<code>{str(e)}</code>")

        async def user_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}user'):
                return

            args = event.text[len(f'{self.prefix}user'):].strip()
            user, _ = await get_user_from_event(event, args)

            if not user:
                if event.is_reply:
                    reply_msg = await event.get_reply_message()
                    user = await self.client.get_entity(reply_msg.sender_id)
                else:
                    user = await self.client.get_me()

            await event.edit("<b>⏳ Сбор детальной информации...</b>")

            try:
                full_user = await self.client(functions.users.GetFullUserRequest(user))
                user_info = full_user.users[0]
                full_info = full_user.full_user

                status = "офлайн"
                if isinstance(user_info.status, types.UserStatusOnline):
                    status = "онлайн 🟢"
                elif isinstance(user_info.status, types.UserStatusRecently):
                    status = "недавно"

                premium = "Да ⭐" if user_info.premium else "Нет"
                bot = "Да 🤖" if user_info.bot else "Нет"
                restricted = "Да 🚫" if user_info.restricted else "Нет"

                text = f"<b>👤 ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:</b>\n"
                text += "─" * 30 + "\n\n"
                text += f"⚜️ <b>Имя:</b> <code>{user_info.first_name or 'Нет'}</code>\n"
                if user_info.last_name:
                    text += f"⚜️ <b>Фамилия:</b> <code>{user_info.last_name}</code>\n"
                text += f"🆔 <b>ID:</b> <code>{user_info.id}</code>\n"
                if user_info.username:
                    text += f"🌐 <b>Username:</b> @{user_info.username}\n"
                if user_info.phone:
                    text += f"📞 <b>Телефон:</b> <code>+{user_info.phone}</code>\n"
                text += f"📡 <b>Статус:</b> <code>{status}</code>\n"
                text += f"⭐ <b>Premium:</b> <code>{premium}</code>\n"
                text += f"🤖 <b>Бот:</b> <code>{bot}</code>\n"
                text += f"🚫 <b>Ограничен:</b> <code>{restricted}</code>\n"
                if full_info.about:
                    text += f"📄 <b>О себе:</b> <code>{full_info.about}</code>\n"
                
                await event.edit(text)
            except Exception as e:
                await event.edit(f"<b>❌ Не удалось собрать информацию:</b>\n<code>{str(e)}</code>")

        client.add_event_handler(ban_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(unban_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(kick_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(mute_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(unmute_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(purge_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(del_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(pin_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(user_handler, events.NewMessage(outgoing=True))
