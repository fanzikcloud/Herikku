from core.base_module import Module
import datetime
import platform
import psutil
import os


class InfoModule(Module):
    NAME = 'Info'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Показывает информацию о пользователе с поддержкой медиа'
    DEPENDENCIES = ['psutil']
    COMMANDS = {'info': 'Показать информацию о себе', 'setinfo':
        'Установить текст (.setinfo <текст>)', 'setinfomedia':
        'Установить медиа (ответьте на гифку/видео командой)'}
    CONFIG_ICON = '👤'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_info':
            info_text = config.get('Info', 'text', fallback='не установлен')
            media_type = config.get('Info', 'media_type', fallback='')
            text = '<b>👤 Info - Настройки</b>\n\n'
            text += f'📝 <b>Текущий текст:</b>\n{info_text}\n\n'
            text += f"""📸 <b>Медиа:</b> {'✅ ' + media_type.upper() if media_type else '❌ Не установлено'}

"""
            text += '<b>Команды для настройки:</b>\n'
            text += f'• <code>.setinfo &lt;текст&gt;</code> - изменить текст\n'
            text += f'• <code>.setinfomedia</code> - установить медиа\n\n'
            text += '<b>Доступные плейсхолдеры:</b>\n'
            text += '• <code>{{name}}</code> - ваше имя\n'
            text += '• <code>{{id}}</code> - ваш ID\n'
            text += '• <code>{{username}}</code> - username\n'
            text += '• <code>{{phone}}</code> - телефон\n'
            text += '• <code>{{time}}</code> - текущее время\n'
            text += '• <code>{{date}}</code> - текущая дата\n'
            text += '• <code>{{uptime}}</code> - время работы бота\n'
            text += '• <code>{{os}}</code> - операционная система\n'
            text += '• <code>{{cpu}}</code> - использование CPU\n'
            text += '• <code>{{ram}}</code> - использование RAM\n'
            text += '• <code>{{python}}</code> - версия Python'
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
        self.bot_start_time = bot_start_time
        if not config.has_section('Info'):
            config.add_section('Info')
            config.set('Info', 'text',
                """👤 **{name}**
🆔 ID: `{id}`
📱 Username: @{username}
⏰ Время: {time}
⏱ Uptime: {uptime}"""
                )
            config.set('Info', 'media_type', '')
            config.set('Info', 'media_id', '')
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)

        async def info_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}info'
                ):
                return
            me = await self.client.get_me()
            info_text = self.config.get('Info', 'text', fallback=
                '👤 **{name}**\n🆔 ID: `{id}`')
            uptime = datetime.datetime.now() - self.bot_start_time
            uptime_str = (
                f'{uptime.days}д {uptime.seconds // 3600}ч {uptime.seconds // 60 % 60}м'
                )
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram_percent = psutil.virtual_memory().percent
            os_info = f'{platform.system()} {platform.release()}'
            python_version = platform.python_version()
            info_text = info_text.replace('{name}', me.first_name or 'Unknown')
            info_text = info_text.replace('{id}', str(me.id))
            info_text = info_text.replace('{username}', me.username or 'нет')
            info_text = info_text.replace('{phone}', me.phone or 'скрыт')
            info_text = info_text.replace('{time}', datetime.datetime.now()
                .strftime('%H:%M:%S'))
            info_text = info_text.replace('{date}', datetime.datetime.now()
                .strftime('%d.%m.%Y'))
            info_text = info_text.replace('{uptime}', uptime_str)
            info_text = info_text.replace('{os}', os_info)
            info_text = info_text.replace('{cpu}', f'{cpu_percent}%')
            info_text = info_text.replace('{ram}', f'{ram_percent}%')
            info_text = info_text.replace('{python}', python_version)
            media_type = self.config.get('Info', 'media_type', fallback='')
            media_path = self.config.get('Info', 'media_id', fallback='')
            if media_type and media_path:
                try:
                    if os.path.exists(media_path):
                        await event.delete()
                        if media_type == 'photo':
                            await self.client.send_file(event.chat_id,
                                media_path, caption=info_text)
                        elif media_type == 'gif':
                            await self.client.send_file(event.chat_id,
                                media_path, caption=info_text, attributes=[
                                ], force_document=False)
                        elif media_type == 'video':
                            await self.client.send_file(event.chat_id,
                                media_path, caption=info_text, attributes=[
                                ], force_document=False)
                    else:
                        await event.edit(
                            f'⚠️ Медиа файл не найден\n\n{info_text}')
                except Exception as e:
                    await event.edit(
                        f"""❌ Ошибка отправки медиа: <code>{str(e)}</code>

{info_text}"""
                        )
            else:
                await event.edit(info_text)

        async def setinfo_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}setinfo'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                current_text = self.config.get('Info', 'text', fallback=
                    'не установлен')
                await event.edit(
                    f"""**📝 Текущий текст:**
{current_text}

**Использование:**
<code>{self.prefix}setinfo &lt;текст&gt;</code>

**Плейсхолдеры:**
• <code>{{name}}</code> - имя
• <code>{{id}}</code> - ID
• <code>{{username}}</code> - username
• <code>{{phone}}</code> - телефон
• <code>{{time}}</code> - время
• <code>{{date}}</code> - дата"""
                    )
                return
            new_text = parts[1]
            self.config.set('Info', 'text', new_text)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            await event.edit(
                f'✅ Текст info обновлен!\n\n<b>Предпросмотр:</b>\n{new_text}')

        async def setinfomedia_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}setinfomedia'):
                return
            if not event.reply_to_msg_id:
                await event.edit(
                    f"""**📸 Установка медиа для info**

Ответьте этой командой на:
• Гифку (GIF)
• Видео
• Фото

Для удаления медиа: `{self.prefix}setinfomedia clear`"""
                    )
                return
            if 'clear' in event.text.lower():
                old_media_path = self.config.get('Info', 'media_id',
                    fallback='')
                if old_media_path and os.path.exists(old_media_path):
                    try:
                        os.remove(old_media_path)
                    except:
                        pass
                self.config.set('Info', 'media_type', '')
                self.config.set('Info', 'media_id', '')
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                await event.edit('✅ Медиа удалено из info')
                return
            reply_msg = await event.get_reply_message()
            if not reply_msg.media:
                await event.edit('❌ Сообщение не содержит медиа')
                return
            try:
                media_file = await reply_msg.download_media(file=bytes)
                if not media_file:
                    await event.edit('❌ Не удалось скачать медиа')
                    return
                media_type = ''
                file_extension = ''
                if reply_msg.gif:
                    media_type = 'gif'
                    file_extension = 'gif'
                elif reply_msg.video:
                    media_type = 'video'
                    file_extension = 'mp4'
                elif reply_msg.photo:
                    media_type = 'photo'
                    file_extension = 'png'
                else:
                    await event.edit(
                        '❌ Поддерживаются только GIF, видео и фото')
                    return
                me = await self.client.get_me()
                user_id = me.id
                old_media_path = self.config.get('Info', 'media_id',
                    fallback='')
                if old_media_path and os.path.exists(old_media_path):
                    try:
                        os.remove(old_media_path)
                    except:
                        pass
                media_path = f'info_media_{user_id}.{file_extension}'
                with open(media_path, 'wb') as f:
                    f.write(media_file)
                self.config.set('Info', 'media_type', media_type)
                self.config.set('Info', 'media_id', os.path.abspath(media_path)
                    )
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                await event.edit(
                    f"""✅ Медиа установлено!
Тип: <b>{media_type.upper()}</b>
Файл: <code>{media_path}</code>"""
                    )
            except Exception as e:
                await event.edit(
                    f'❌ Ошибка сохранения медиа: <code>{str(e)}</code>')
        client.add_event_handler(info_handler, events.NewMessage(outgoing=True)
            )
        client.add_event_handler(setinfo_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(setinfomedia_handler, events.NewMessage(
            outgoing=True))
