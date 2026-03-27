from core.base_module import Module
import asyncio
import datetime
TIMEZONE_OFFSETS = {'MSK': 3, 'EKB': 5, 'UTC': 0, 'GMT': 0, 'CET': 1, 'EET':
    2, 'AZT': 4, 'AMT': 4, 'GET': 4, 'TJT': 5, 'TMT': 5, 'UZT': 5, 'KGT': 6,
    'BDT': 6, 'IST': 5.5, 'THA': 7, 'ICT': 7, 'CST': 8, 'HKT': 8, 'JST': 9,
    'KST': 9, 'EST': -5, 'EDT': -4, 'CDT': -5, 'MDT': -6, 'PDT': -7, 'PST':
    -8, 'AKST': -9, 'AEST': 10, 'NZST': 12, 'IRKTSK': 8}
FONT_STYLES = {(1): lambda x: x, (2): lambda x: f'『{x}』', (3): lambda x: x.
    translate(str.maketrans('0123456789', '⓿➊➋➌➍➎➏➐➑➒')), (4): lambda x: x.
    translate(str.maketrans('0123456789', '⓪⓵⓶⓷⓸⓹⓺⓻⓼⓽')), (5): lambda x: x.
    translate(str.maketrans('0123456789', '⓪①②③④⑤⑥⑦⑧⑨')), (6): lambda x: x.
    translate(str.maketrans('0123456789', '𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡')), (7): lambda x: x.
    translate(str.maketrans('0123456789:', "⁰¹²³⁴⁵⁶⁷⁸⁹'")), (8): lambda x:
    x.translate(str.maketrans('0123456789:', '₀₁₂₃₄₅₆₇₈₉‚')), (9): lambda x:
    ''.join([(i + '️⃣' if i.isdigit() else i) for i in x])}


class TimeInNickModule(Module):
    NAME = 'TimeInNick'
    AUTHOR = 'Toxano (adapted for Herikku)'
    DESCRIPTION = (
        'Показывает текущее время в никнейме и био с разными стилями шрифтов')
    DEPENDENCIES = []
    COMMANDS = {'timenick': 'Включить/выключить время в никнейме',
        'timebio': 'Включить/выключить время в био', 'timetz':
        'Установить часовой пояс (например: .timetz MSK)', 'timestyle':
        'Установить стиль шрифта 1-9 (например: .timestyle 2)',
        'timeformat':
        'Установить формат никнейма (например: .timeformat {nickname} | {time})'
        }
    CONFIG_ICON = '⏰'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_time_in_nick':
            nick_active = config.get('TimeInNick', 'nick_active', fallback='no'
                )
            bio_active = config.get('TimeInNick', 'bio_active', fallback='no')
            timezone = config.get('TimeInNick', 'timezone', fallback='MSK')
            font_style = config.get('TimeInNick', 'font_style', fallback='1')
            update_delay = config.get('TimeInNick', 'update_delay',
                fallback='60')
            text = '<b>⏰ TimeInNick - Настройки</b>\n\n'
            text += (
                f"📝 Никнейм: {'✅ Включен' if nick_active == 'yes' else '❌ Выключен'}\n"
                )
            text += (
                f"📄 Био: {'✅ Включен' if bio_active == 'yes' else '❌ Выключен'}\n"
                )
            text += f'🌍 Часовой пояс: <code>{timezone}</code>\n'
            text += f'🎨 Стиль шрифта: <code>{font_style}</code>\n'
            text += f'⏱ Обновление: <code>{update_delay}</code> сек\n\n'
            text += '<b>Команды для настройки:</b>\n'
            text += f'• <code>.timenick</code> - вкл/выкл время в нике\n'
            text += f'• <code>.timebio</code> - вкл/выкл время в био\n'
            text += f'• <code>.timetz &lt;пояс&gt;</code> - изменить пояс\n'
            text += f'• <code>.timestyle &lt;1-9&gt;</code> - изменить стиль\n'
            buttons = [[Button.inline('🌍 Часовые пояса',
                b'timenick_timezones')], [Button.inline('🎨 Стили шрифтов',
                b'timenick_styles')], [Button.inline('◀️ К модулям',
                b'settings_modules')]]
            await event.edit(text, buttons=buttons)
        elif data == 'timenick_timezones':
            text = '<b>🌍 Доступные часовые пояса:</b>\n\n'
            text += '🇷🇺 <b>Россия:</b>\n'
            text += '• <code>MSK</code> - Москва (UTC+3)\n'
            text += '• <code>EKB</code> - Екатеринбург (UTC+5)\n'
            text += '• <code>IRKTSK</code> - Иркутск (UTC+8)\n\n'
            text += '🌍 <b>Другие:</b>\n'
            text += '• <code>UTC</code> / <code>GMT</code> - UTC+0\n'
            text += '• <code>CET</code> - Центральная Европа (UTC+1)\n'
            text += '• <code>EET</code> - Восточная Европа (UTC+2)\n'
            text += '• <code>AZT</code> - Азербайджан (UTC+4)\n'
            text += '• <code>IST</code> - Индия (UTC+5:30)\n'
            text += '• <code>CST</code> - Китай (UTC+8)\n'
            text += '• <code>JST</code> - Япония (UTC+9)\n'
            text += '• <code>PST</code> - США Запад (UTC-8)\n'
            text += '• <code>EST</code> - США Восток (UTC-5)\n\n'
            text += 'Используйте: <code>.timetz &lt;код&gt;</code>'
            buttons = [[Button.inline('◀️ Назад', b'module_time_in_nick')]]
            await event.edit(text, buttons=buttons)
        elif data == 'timenick_styles':
            text = '<b>🎨 Доступные стили шрифтов:</b>\n\n'
            text += '1️⃣ <code>12:34</code> - обычный\n'
            text += '2️⃣ <code>『12:34』</code> - в скобках\n'
            text += '3️⃣ <code>➊➋:➌➍</code> - кружки с цифрами\n'
            text += '4️⃣ <code>⓵⓶:⓷⓸</code> - двойные кружки\n'
            text += '5️⃣ <code>①②:③④</code> - простые кружки\n'
            text += '6️⃣ <code>𝟙𝟚:𝟛𝟜</code> - жирные цифры\n'
            text += "7️⃣ <code>¹²'³⁴</code> - верхний индекс\n"
            text += '8️⃣ <code>₁₂‚₃₄</code> - нижний индекс\n'
            text += '9️⃣ <code>1️⃣2️⃣:3️⃣4️⃣</code> - эмодзи цифры\n\n'
            text += 'Используйте: <code>.timestyle &lt;1-9&gt;</code>'
            buttons = [[Button.inline('◀️ Назад', b'module_time_in_nick')]]
            await event.edit(text, buttons=buttons)
        else:
            raise Exception('Not our callback')

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        from telethon.tl.functions.account import UpdateProfileRequest
        from telethon.tl.functions.users import GetFullUserRequest
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.config_path = config_path
        self.UpdateProfileRequest = UpdateProfileRequest
        self.GetFullUserRequest = GetFullUserRequest
        if not config.has_section('TimeInNick'):
            config.add_section('TimeInNick')
            config.set('TimeInNick', 'timezone', 'MSK')
            config.set('TimeInNick', 'update_delay', '60')
            config.set('TimeInNick', 'nick_format', '{nickname} | {time}')
            config.set('TimeInNick', 'bio_format', '{bio} | {time}')
            config.set('TimeInNick', 'font_style', '1')
            config.set('TimeInNick', 'nick_active', 'no')
            config.set('TimeInNick', 'bio_active', 'no')
            config.set('TimeInNick', 'original_nick', '')
            config.set('TimeInNick', 'original_bio', '')
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
        self.nick_active = config.getboolean('TimeInNick', 'nick_active',
            fallback=False)
        self.bio_active = config.getboolean('TimeInNick', 'bio_active',
            fallback=False)
        self.nick_task = None
        self.bio_task = None
        self.last_nick_time = None
        self.last_bio_time = None
        if self.nick_active:
            self.nick_task = asyncio.create_task(self._update_nickname())
        if self.bio_active:
            self.bio_task = asyncio.create_task(self._update_bio())

        async def timenick_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}timenick'):
                return
            if self.nick_active:
                self.nick_active = False
                if self.nick_task:
                    self.nick_task.cancel()
                    self.nick_task = None
                original_nick = self.config.get('TimeInNick',
                    'original_nick', fallback='')
                if original_nick:
                    try:
                        await self.client(self.UpdateProfileRequest(
                            first_name=original_nick[:70]))
                    except:
                        pass
                self.config.set('TimeInNick', 'nick_active', 'no')
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                await event.edit('⏰ Отображение времени в никнейме выключено')
            else:
                me = await self.client.get_me()
                current_nick = me.first_name or 'User'
                if '|' in current_nick:
                    original_nick = current_nick.split('|')[0].strip()
                else:
                    original_nick = current_nick
                self.config.set('TimeInNick', 'original_nick', original_nick)
                self.config.set('TimeInNick', 'nick_active', 'yes')
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                self.nick_active = True
                self.nick_task = asyncio.create_task(self._update_nickname())
                await event.edit('⏰ Отображение времени в никнейме включено')

        async def timebio_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}timebio'):
                return
            if self.bio_active:
                self.bio_active = False
                if self.bio_task:
                    self.bio_task.cancel()
                    self.bio_task = None
                original_bio = self.config.get('TimeInNick', 'original_bio',
                    fallback='')
                try:
                    await self.client(self.UpdateProfileRequest(about=
                        original_bio[:70]))
                except:
                    pass
                self.config.set('TimeInNick', 'bio_active', 'no')
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                await event.edit('⏰ Отображение времени в био выключено')
            else:
                try:
                    full_user = await self.client(self.GetFullUserRequest('me')
                        )
                    current_bio = full_user.full_user.about or ''
                    if '|' in current_bio:
                        original_bio = current_bio.split('|')[0].strip()
                    else:
                        original_bio = current_bio
                    self.config.set('TimeInNick', 'original_bio', original_bio)
                    self.config.set('TimeInNick', 'bio_active', 'yes')
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        self.config.write(f)
                    self.bio_active = True
                    self.bio_task = asyncio.create_task(self._update_bio())
                    await event.edit('⏰ Отображение времени в био включено')
                except Exception as e:
                    await event.edit(f'❌ Ошибка: {str(e)}')

        async def timetz_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}timetz'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                tz_list = ', '.join(TIMEZONE_OFFSETS.keys())
                current_tz = self.config.get('TimeInNick', 'timezone',
                    fallback='MSK')
                await event.edit(
                    f"""**Текущий часовой пояс:** `{current_tz}`

**Доступные пояса:**
{tz_list}"""
                    )
                return
            new_tz = parts[1].strip().upper()
            if new_tz not in TIMEZONE_OFFSETS:
                await event.edit(
                    f"❌ Неверный часовой пояс. Используйте: {', '.join(TIMEZONE_OFFSETS.keys())}"
                    )
                return
            self.config.set('TimeInNick', 'timezone', new_tz)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            await event.edit(f'✅ Часовой пояс установлен: `{new_tz}`')

        async def timestyle_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}timestyle'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                current_style = self.config.get('TimeInNick', 'font_style',
                    fallback='1')
                styles_desc = '1-9: разные стили шрифтов'
                await event.edit(
                    f'**Текущий стиль:** `{current_style}`\n\n{styles_desc}')
                return
            try:
                style = int(parts[1].strip())
                if style < 1 or style > 9:
                    await event.edit('❌ Стиль должен быть от 1 до 9')
                    return
                self.config.set('TimeInNick', 'font_style', str(style))
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                await event.edit(f'✅ Стиль шрифта установлен: `{style}`')
            except ValueError:
                await event.edit('❌ Введите число от 1 до 9')

        async def timeformat_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}timeformat'):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                current_format = self.config.get('TimeInNick',
                    'nick_format', fallback='{nickname} | {time}')
                await event.edit(
                    f"""**Текущий формат:** `{current_format}`

**Переменные:** {{nickname}}, {{time}}"""
                    )
                return
            new_format = parts[1].strip()
            self.config.set('TimeInNick', 'nick_format', new_format)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            await event.edit(f'✅ Формат установлен: `{new_format}`')
        client.add_event_handler(timenick_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(timebio_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(timetz_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(timestyle_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(timeformat_handler, events.NewMessage(
            outgoing=True))

    async def get_formatted_time(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        timezone = self.config.get('TimeInNick', 'timezone', fallback='MSK'
            ).upper()
        if timezone not in TIMEZONE_OFFSETS:
            timezone = 'UTC'
        offset = TIMEZONE_OFFSETS[timezone]
        hour_offset = int(offset)
        minute_offset = int((offset - hour_offset) * 60)
        adjusted_time = now + datetime.timedelta(hours=hour_offset, minutes
            =minute_offset)
        time_str = adjusted_time.strftime('%H:%M')
        font_style = int(self.config.get('TimeInNick', 'font_style',
            fallback='1'))
        if font_style not in FONT_STYLES:
            font_style = 1
        return FONT_STYLES[font_style](time_str)

    async def _update_nickname(self):
        update_delay = int(self.config.get('TimeInNick', 'update_delay',
            fallback='60'))
        while self.nick_active:
            try:
                current_time = await self.get_formatted_time()
                if current_time != self.last_nick_time:
                    original_nick = self.config.get('TimeInNick',
                        'original_nick', fallback='User')
                    nick_format = self.config.get('TimeInNick',
                        'nick_format', fallback='{nickname} | {time}')
                    new_nick = nick_format.format(nickname=original_nick,
                        time=current_time)
                    await self.client(self.UpdateProfileRequest(first_name=
                        new_nick[:70]))
                    self.last_nick_time = current_time
            except Exception as e:
                print(f'Ошибка обновления никнейма: {e}')
            await asyncio.sleep(update_delay)

    async def _update_bio(self):
        update_delay = int(self.config.get('TimeInNick', 'update_delay',
            fallback='60'))
        while self.bio_active:
            try:
                current_time = await self.get_formatted_time()
                if current_time != self.last_bio_time:
                    original_bio = self.config.get('TimeInNick',
                        'original_bio', fallback='')
                    bio_format = self.config.get('TimeInNick', 'bio_format',
                        fallback='{bio} | {time}')
                    new_bio = bio_format.format(bio=original_bio, time=
                        current_time)
                    await self.client(self.UpdateProfileRequest(about=
                        new_bio[:70]))
                    self.last_bio_time = current_time
            except Exception as e:
                print(f'Ошибка обновления био: {e}')
            await asyncio.sleep(update_delay)

    async def dispose(self):
        if self.nick_task:
            self.nick_task.cancel()
        if self.bio_task:
            self.bio_task.cancel()
        if self.nick_active:
            original_nick = self.config.get('TimeInNick', 'original_nick',
                fallback='')
            if original_nick:
                try:
                    await self.client(self.UpdateProfileRequest(first_name=
                        original_nick[:70]))
                except:
                    pass
        if self.bio_active:
            original_bio = self.config.get('TimeInNick', 'original_bio',
                fallback='')
            try:
                await self.client(self.UpdateProfileRequest(about=
                    original_bio[:70]))
            except:
                pass
