from core.base_module import Module
import datetime
import platform
import psutil
import os
import time
import asyncio
import json
from core.formatting import markdown_to_html


class InfoModule(Module):
    NAME = 'Info'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Показывает информацию о пользователе через inline-бота с поддержкой медиа, плейсхолдеров, форматирования и кастомных кнопок-ссылок или алертов'
    DEPENDENCIES = ['psutil']
    COMMANDS = {
        'info': 'Показать информацию о себе через inline-бота',
        'setinfo <текст>': 'Установить текст (.setinfo <текст>)',
        'setinfomedia': 'Установить медиа (ответьте на гифку/видео/фото)',
        'setinfobtn <название> | <ссылка/текст>': 'Добавить кнопку с ссылкой или всплывающим алертом под инфо (или clear для сброса)'
    }
    CONFIG_ICON = '👤'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_info':
            info_text = config.get('Info', 'text', fallback='не установлен')
            media_type = config.get('Info', 'media_type', fallback='')
            btn_data = config.get('Info', 'button', fallback='{}')
            
            btn_info = "нет"
            try:
                btn_dict = json.loads(btn_data)
                if btn_dict:
                    btn_type = "Ссылка" if btn_dict.get('is_url', True) else "Текст/Алерт"
                    only_owner = "только владелец" if btn_dict.get('only_owner', False) else "все"
                    btn_info = f"<code>{btn_dict['text']}</code> ({btn_type}, {only_owner}) -> {btn_dict['value']}"
            except:
                pass

            text = '<b>👤 Info - Настройки</b>\n\n'
            text += f'📝 <b>Текущий текст:</b>\n{info_text}\n\n'
            text += f"📸 <b>Медиа:</b> {'✅ ' + media_type.upper() if media_type else '❌ Не установлено'}\n"
            text += f"🔗 <b>Кнопка:</b> {btn_info}\n\n"
            text += '<b>Команды для настройки:</b>\n'
            text += f'• <code>.setinfo &lt;текст&gt;</code> - изменить текст\n'
            text += f'• <code>.setinfomedia</code> - установить медиа\n'
            text += f'• <code>.setinfobtn Название | ссылка или текст</code> - добавить кнопку\n'
            text += f'• <code>.setinfobtn clear</code> - удалить кнопку\n\n'
            text += '<b>Доступные плейсхолдеры:</b>\n'
            text += '• <code>{name}</code> - ваше имя\n'
            text += '• <code>{id}</code> - ваш ID\n'
            text += '• <code>{username}</code> - username\n'
            text += '• <code>{phone}</code> - телефон\n'
            text += '• <code>{time}</code> - текущее время\n'
            text += '• <code>{date}</code> - текущая дата\n'
            text += '• <code>{uptime}</code> - время работы бота\n'
            text += '• <code>{sys_uptime}</code> - аптайм системы\n'
            text += '• <code>{os}</code> - операционная система\n'
            text += '• <code>{cpu}</code> - использование CPU\n'
            text += '• <code>{ram}</code> - использование RAM\n'
            text += '• <code>{gpu}</code> - видеокарта\n'
            text += '• <code>{ping}</code> - пинг Telegram\n'
            text += '• <code>{python}</code> - версия Python\n'
            text += '• <code>{version}</code> - версия Herikku'
            buttons = [[Button.inline('◀️ К модулям', b'settings_modules')]]
            await event.edit(text, buttons=buttons)
        else:
            raise Exception('Not our callback')

    @staticmethod
    async def INLINE_HANDLERS(bot_client, events, config, loaded_modules):
        from telethon import Button
        owner_id = None

        @bot_client.on(events.InlineQuery)
        async def info_inline_query(event):
            nonlocal owner_id
            query = event.text.strip().lower()
            if query != 'info_inline':
                return
            if owner_id is None:
                owner_id = event.sender_id
            if event.sender_id != owner_id:
                await event.answer([])
                return
                
            builder = event.builder
            
            # Рендерим текст
            start_ping = datetime.datetime.now()
            try:
                await bot_client.get_me()
            except:
                pass
            end_ping = datetime.datetime.now()
            ping_ms = (end_ping - start_ping).total_seconds() * 1000

            # Подтягиваем оригинального клиента юзербота из загруженных модулей
            user_client = None
            for m in loaded_modules.values():
                if hasattr(m, 'client') and m.client:
                    user_client = m.client
                    break
                    
            if not user_client:
                user_client = bot_client
                    
            try:
                me = await user_client.get_me()
            except:
                me = await bot_client.get_me()
                
            info_text = config.get('Info', 'text', fallback='👤 **{name}**\n🆔 ID: `{id}`')
            bot_start_time_str = config.get('Settings', 'bot_start_time_ts', fallback=str(time.time()))
            try:
                bot_start_time = datetime.datetime.fromtimestamp(float(bot_start_time_str))
            except:
                bot_start_time = datetime.datetime.now()

            uptime = datetime.datetime.now() - bot_start_time
            uptime_str = f'{uptime.days}д {uptime.seconds // 3600}ч {uptime.seconds // 60 % 60}м'
            
            try:
                boot_time_timestamp = psutil.boot_time()
                sys_uptime_seconds = time.time() - boot_time_timestamp
                sys_days = int(sys_uptime_seconds // (24 * 3600))
                sys_hours = int((sys_uptime_seconds % (24 * 3600)) // 3600)
                sys_minutes = int((sys_uptime_seconds % 3600) // 60)
                sys_uptime_str = f'{sys_days}д {sys_hours}ч {sys_minutes}м'
            except:
                sys_uptime_str = uptime_str
                
            cpu_percent = psutil.cpu_percent(interval=None)
            if cpu_percent == 0.0:
                cpu_percent = psutil.cpu_percent(interval=0.05)
                
            ram_percent = psutil.virtual_memory().percent
            os_info = f'{platform.system()} {platform.release()}'
            python_version = platform.python_version()
            bot_version = '1.0.0'
            
            # Получение видеокарты
            gpu_info = 'Не найдено/встроенная'
            try:
                if platform.system() == 'Windows':
                    import subprocess
                    cmd = 'wmic path win32_VideoController get name'
                    out = subprocess.check_output(cmd, shell=True).decode('cp1251', errors='ignore')
                    lines = [line.strip() for line in out.splitlines() if line.strip()]
                    if len(lines) > 1:
                        gpu_info = lines[1]
                elif platform.system() == 'Linux':
                    import subprocess
                    try:
                        out = subprocess.check_output("lspci | grep -i 'vga\\|3d\\|display'", shell=True).decode('utf-8', errors='ignore')
                        if out:
                            parts = out.split(':')
                            if len(parts) > 2:
                                gpu_info = parts[2].strip()
                    except:
                        pass
            except:
                pass
            
            for placeholder, value in [
                ('name', me.first_name or 'Unknown'),
                ('id', str(me.id)),
                ('username', me.username or 'нет'),
                ('phone', me.phone or 'скрыт'),
                ('time', datetime.datetime.now().strftime('%H:%M:%S')),
                ('date', datetime.datetime.now().strftime('%d.%m.%Y')),
                ('uptime', uptime_str),
                ('sys_uptime', sys_uptime_str),
                ('os', os_info),
                ('cpu', f'{cpu_percent}%'),
                ('ram', f'{ram_percent}%'),
                ('gpu', gpu_info),
                ('ping', f'{ping_ms:.1f}ms'),
                ('python', python_version),
                ('version', bot_version)
            ]:
                info_text = info_text.replace(f'{{{placeholder}}}', value)
                info_text = info_text.replace(f'{{{{{placeholder}}}}}', value)
                
            info_text = markdown_to_html(info_text)
            
            # Очищаем экранирование обратных слешей из конфига, если они попали туда при чтении
            info_text = info_text.replace('\\"', '"').replace('\\/', '/')
            
            # Кастомная кнопка (ссылка или алерт)
            buttons = []
            btn_data = config.get('Info', 'button', fallback='{}')
            btn_dict = {}
            try:
                btn_dict = json.loads(btn_data)
                if btn_dict and 'text' in btn_dict and 'value' in btn_dict:
                    if btn_dict.get('is_url', True):
                        buttons.append([Button.url(btn_dict['text'], btn_dict['value'])])
                    else:
                        # Текстовая кнопка с callback-датой
                        buttons.append([Button.inline(btn_dict['text'], b'infobtn_alert')])
            except:
                pass
            
            # Обработка медиа
            media_type = config.get('Info', 'media_type', fallback='')
            media_path = config.get('Info', 'media_id', fallback='')
            
            if media_type and media_path and os.path.exists(media_path):
                result = builder.photo(
                    file=media_path,
                    text=info_text,
                    buttons=buttons if buttons else None
                )
            else:
                # Обычная статья (article) для отправки текстового сообщения с кастомными кнопками
                # НЕ передаем аргумент url в builder.article, чтобы Telegram отправил полноценное сообщение
                # в чат с прикрепленной к нему нативной URL-кнопкой Button.url!
                result = builder.article(
                    title='👤 Информация о пользователе',
                    text=info_text,
                    buttons=buttons if buttons else None
                )
                
            await event.answer([result], cache_time=0)

        # Обработчик клика по callback-кнопке (показ алертом кастомного текста)
        @bot_client.on(events.CallbackQuery(pattern=b'infobtn_alert'))
        async def infobtn_alert_handler(event):
            btn_data = config.get('Info', 'button', fallback='{}')
            try:
                btn_dict = json.loads(btn_data)
                if btn_dict and 'value' in btn_dict:
                    only_owner = btn_dict.get('only_owner', False)
                    # Если включено ограничение "только владелец", сверяем ID кликнувшего с владельцем
                    if only_owner and event.sender_id != owner_id:
                        await event.answer('🔒 Доступ к этой кнопке разрешен только владельцу юзербота!', alert=True)
                        return
                    await event.answer(btn_dict['value'], alert=True)
                else:
                    await event.answer('Информация отсутствует', alert=True)
            except Exception as e:
                await event.answer(f'Ошибка: {e}', alert=True)

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.config_path = config_path
        self.bot_start_time = bot_start_time
        
        if not config.has_option('Settings', 'bot_start_time_ts'):
            config.set('Settings', 'bot_start_time_ts', str(bot_start_time.timestamp()))
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
        if not config.has_section('Info'):
            config.add_section('Info')
            config.set('Info', 'text',
                """👤 **{name}**
🆔 ID: `{id}`
📱 Username: @{username}
⏰ Время: {time}
⏱ Uptime бота: {uptime}
⚙️ OS: {os}
⚡ Ping: {ping}"""
                )
            config.set('Info', 'media_type', '')
            config.set('Info', 'media_id', '')
            config.set('Info', 'button', '{}')
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)

        async def info_handler(event):
            if not event.text:
                return
            if event.text.strip() != f'{self.prefix}info':
                return
            bot_username = self.config.get('InlineBot', 'username', fallback='')
            bot_token = self.config.get('InlineBot', 'token', fallback='')
            if not bot_username or not bot_token:
                await event.edit('❌ Inline-бот не настроен!')
                return
            try:
                bot = await self.client.get_entity(bot_username)
                result = await self.client.inline_query(bot, 'info_inline')
                if result:
                    await result[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
                    await event.delete()
                else:
                    await event.edit('❌ Бот не вернул результатов!')
            except Exception as e:
                # В случае клика по прямой ссылке, результат открывается на стороне клиента без отправки сообщения.
                # Метод .click() на стороне API может вернуть ошибку, если это чистый URL-результат, предназначенный для открытия,
                # а не для отправки сообщения. Погасим ошибку удаления, если все прошло успешно.
                try:
                    await event.delete()
                except:
                    pass

        async def setinfo_handler(event):
            if not event.text:
                return
            if not (event.text.startswith(f'{self.prefix}setinfo ') or event.text.strip() == f'{self.prefix}setinfo'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                current_text = self.config.get('Info', 'text', fallback='не установлен')
                await event.edit(f"📝 Текущий текст:\n{current_text}")
                return
            new_text = parts[1]
            self.config.set('Info', 'text', new_text)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            await event.edit('✅ Шаблон info обновлен!')

        async def setinfobtn_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}setinfobtn'):
                return
            args = event.text[len(f'{self.prefix}setinfobtn '):].strip()
            if not args:
                await event.edit(
                    f"""<b>🔗 Настройка inline-кнопки под Info</b>

<b>Использование:</b>
<code>{self.prefix}setinfobtn Название | ссылка_или_текст [| owner/all]</code>

<b>Пример 1 (Ссылка для всех):</b>
<code>{self.prefix}setinfobtn Мой канал | https://t.me/my_channel</code>

<b>Пример 2 (Алерт только для Вас):</b>
<code>{self.prefix}setinfobtn Привет | Я создатель этого юзербота! | owner</code>

<b>Пример 3 (Алерт для всех):</b>
<code>{self.prefix}setinfobtn Привет | Рад всех видеть! | all</code>

Для сброса: <code>{self.prefix}setinfobtn clear</code>"""
                )
                return
                
            if args.lower() == 'clear':
                self.config.set('Info', 'button', '{}')
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                await event.edit('✅ Inline-кнопка удалена из Info!')
                return
                
            if '|' not in args:
                await event.edit('❌ Неверный формат! Используйте разделитель |')
                return
                
            parts = [p.strip() for p in args.split('|')]
            name = parts[0]
            value = parts[1]
            
            # По умолчанию кнопка доступна всем
            only_owner = False
            if len(parts) > 2:
                mode = parts[2].lower()
                if mode == 'owner':
                    only_owner = True
            
            # Проверяем, является ли значение ссылкой
            is_url = False
            # Пытаемся определить ссылки с протоколами или юзернеймами (@username, t.me/...)
            clean_val = value.lower()
            if (clean_val.startswith('http://') or 
                clean_val.startswith('https://') or 
                clean_val.startswith('tg://') or 
                clean_val.startswith('@') or 
                clean_val.startswith('t.me/')):
                is_url = True
                # Если ссылка начинается без протокола, но это юзернейм или t.me,
                # отформатируем её правильно для Telethon Button.url
                if clean_val.startswith('@'):
                    value = f"https://t.me/{value[1:]}"
                elif clean_val.startswith('t.me/'):
                    value = f"https://{value}"
                
            btn_dict = {'text': name, 'value': value, 'is_url': is_url, 'only_owner': only_owner}
            self.config.set('Info', 'button', json.dumps(btn_dict, ensure_ascii=False))
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
                
            type_str = "ссылка" if is_url else f"всплывающий текст ({'только для вас' if only_owner else 'для всех'})"
            await event.edit(f'✅ Кнопка «<b>{name}</b>» ({type_str}) успешно добавлена под Info!')

        async def setinfomedia_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}setinfomedia'):
                return
            if not event.reply_to_msg_id:
                await event.edit(
                    f"""**📸 Установка медиа для info**
Ответьте этой командой на гифку, фото или видео.
Для удаления: `{self.prefix}setinfomedia clear`"""
                )
                return
                
            if 'clear' in event.text.lower():
                old_media_path = self.config.get('Info', 'media_id', fallback='')
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
            if not reply_msg or not reply_msg.media:
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
                    await event.edit('❌ Поддерживаются только GIF, видео и фото')
                    return
                    
                me = await self.client.get_me()
                user_id = me.id
                old_media_path = self.config.get('Info', 'media_id', fallback='')
                if old_media_path and os.path.exists(old_media_path):
                    try:
                        os.remove(old_media_path)
                    except:
                        pass
                media_path = f'info_media_{user_id}.{file_extension}'
                with open(media_path, 'wb') as f:
                    f.write(media_file)
                    
                self.config.set('Info', 'media_type', media_type)
                self.config.set('Info', 'media_id', os.path.abspath(media_path))
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                    
                await event.edit(f'✅ Медиа ({media_type.upper()}) успешно добавлено!')
            except Exception as e:
                await event.edit(f'❌ Ошибка сохранения медиа: {str(e)}')

        client.add_event_handler(info_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(setinfo_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(setinfobtn_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(setinfomedia_handler, events.NewMessage(outgoing=True))
