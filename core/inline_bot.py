import configparser
from telethon import TelegramClient, events, Button
from core.text_formatter import TextFormatter
from core.config_manager import save_account_config


async def start_account_bot(user_id, bot_token, api_id, api_hash, proxy,
    account_config, account_modules, account_bots, account_configs):
    try:
        bot_session_name = f'inline_bot_session_{user_id}'
        bot_client = TelegramClient(bot_session_name, api_id, api_hash,
            proxy=proxy)
        await bot_client.start(bot_token=bot_token)
        from telethon.extensions import html
        bot_client.parse_mode = html
        from core.formatting import markdown_to_html
        original_edit = bot_client.edit_message

        async def patched_edit(*args, **kwargs):
            args_list = list(args)
            if len(args_list) >= 2:
                if isinstance(args_list[1], str):
                    args_list[1] = markdown_to_html(args_list[1])
                elif len(args_list) >= 3 and isinstance(args_list[2], str):
                    args_list[2] = markdown_to_html(args_list[2])
            if 'message' in kwargs and isinstance(kwargs['message'], str):
                kwargs['message'] = markdown_to_html(kwargs['message'])
            if 'text' in kwargs and isinstance(kwargs['text'], str):
                kwargs['text'] = markdown_to_html(kwargs['text'])
            return await original_edit(*args_list, **kwargs)
        bot_client.edit_message = patched_edit
        bot_me = await bot_client.get_me()
        bot_username = bot_me.username
        if not account_config.get('InlineBot', 'username', fallback=''):
            account_config.set('InlineBot', 'username', bot_username)
            account_config.set('InlineBot', 'name', bot_me.first_name)
            save_account_config(user_id, account_configs)
        print(TextFormatter.color(
            f'🤖 Inline-бот запущен для аккаунта {user_id}: @{bot_username}',
            'green'))
        await start_inline_bot_handler(bot_client, account_config, user_id,
            account_modules)
        user_modules = account_modules.get(user_id, {})
        for module_name, module_instance in user_modules.items():
            if hasattr(module_instance, 'INLINE_HANDLERS'
                ) and module_instance.INLINE_HANDLERS:
                try:
                    await module_instance.INLINE_HANDLERS(bot_client,
                        events, account_config, user_modules)
                    print(TextFormatter.color(
                        f'🔗 Inline-обработчики зарегистрированы для {module_instance.NAME} (аккаунт {user_id})'
                        , 'cyan'))
                except Exception as e:
                    print(TextFormatter.color(
                        f'⚠️ Ошибка регистрации inline-обработчиков для {module_instance.NAME}: {e}'
                        , 'yellow'))
        account_bots[user_id] = bot_client
        return bot_client
    except Exception as e:
        print(TextFormatter.color(
            f'⚠️ Не удалось запустить inline-бота для аккаунта {user_id}: {e}',
            'yellow'))
        return None


async def start_inline_bot_handler(bot, config, user_id, account_modules):
    owner_id = user_id
    user_modules = account_modules.get(user_id, {})
    print(TextFormatter.color(f'🔒 Inline-бот защищен. Владелец: {owner_id}',
        'cyan'))

    @bot.on(events.NewMessage)
    async def private_message_handler(event):
        if not event.is_private:
            return
        if event.sender_id == owner_id:
            return
        try:
            user = await event.get_sender()
            username = f'@{user.username}' if user.username else 'без username'
            user_name = user.first_name or 'Unknown'
            print(TextFormatter.color(
                f'⚠️  Личное сообщение боту (аккаунт {user_id}): {user_name} ({username}, ID: {event.sender_id})'
                , 'yellow'))
        except:
            print(TextFormatter.color(
                f'⚠️  Личное сообщение боту (аккаунт {user_id}) от ID: {event.sender_id}'
                , 'yellow'))
        import os
        banner_path = 'core/assets/img/banner.jpg'
        text = """🤖 <b>Herikku Userbot</b>

⚠️ This bot is private!

Get your own: <a href='https://github.com/fanzikcloud/Herikku'>GitHub</a>"""
        try:
            if os.path.exists(banner_path):
                await event.respond(file=banner_path, message=text)
            else:
                await event.respond(text)
        except Exception as e:
            print(TextFormatter.color(f'⚠️  Ошибка отправки сообщения: {e}',
                'yellow'))
            await event.respond(text)

    @bot.on(events.InlineQuery)
    async def inline_handler(event):
        print(TextFormatter.color(
            f"📨 Inline-запрос получен: sender_id={event.sender_id}, owner_id={owner_id}, query='{event.text}'"
            , 'cyan'))
        if event.sender_id != owner_id:
            try:
                user = await event.get_sender()
                username = (f'@{user.username}' if user.username else
                    'без username')
                user_name = user.first_name or 'Unknown'
                print(TextFormatter.color(
                    f'⚠️  Попытка доступа к inline-боту (аккаунт {user_id}): {user_name} ({username}, ID: {event.sender_id})'
                    , 'yellow'))
            except:
                print(TextFormatter.color(
                    f'⚠️  Попытка доступа к inline-боту (аккаунт {user_id}) от ID: {event.sender_id}'
                    , 'yellow'))
            builder = event.builder
            text = """🤖 <b>Herikku Userbot</b>

⚠️ This bot is private!

Get your own: <a href='https://github.com/fanzikcloud/Herikku'>GitHub</a>"""
            import os
            banner_path = 'core/assets/img/banner.jpg'
            try:
                if os.path.exists(banner_path):
                    result = builder.photo(file=banner_path, text=text,
                        buttons=[[Button.url('📦 Get Herikku',
                        'https://github.com/fanzikcloud/Herikku')]])
                else:
                    result = builder.article(title=
                        '🤖 Herikku Userbot - Private', text=text, buttons=[
                        [Button.url('📦 Get Herikku',
                        'https://github.com/fanzikcloud/Herikku')]])
                await event.answer([result], cache_time=0)
            except Exception as e:
                print(TextFormatter.color(
                    f'⚠️  Ошибка отправки баннера: {e}', 'yellow'))
                result = builder.article(title=
                    '🤖 Herikku Userbot - Private', text=text, buttons=[[
                    Button.url('📦 Get Herikku',
                    'https://github.com/fanzikcloud/Herikku')]])
                await event.answer([result], cache_time=0)
            return
        print(TextFormatter.color(
            f'✅ Владелец использует inline-бот (аккаунт {user_id})', 'green'))
        query = event.text.strip().lower()
        if query and query != 'config':
            return
        builder = event.builder
        buttons = [[Button.inline('⚙️ Общие настройки', b'settings_general'
            )], [Button.inline('🔧 Префикс команд', b'settings_prefix')], [
            Button.inline('📦 Модули', b'settings_modules')], [Button.inline
            ('🌐 Прокси', b'settings_proxy')], [Button.inline(
            'ℹ️ Информация', b'settings_info')]]
        result = builder.article(title='⚙️ Настройки Herikku', text=
            """<b>⚙️ Меню настроек Herikku Userbot</b>

Выберите раздел для настройки:"""
            , buttons=buttons)
        await event.answer([result])

    @bot.on(events.CallbackQuery)
    async def callback_handler(event):
        if event.sender_id != owner_id:
            await event.answer('❌ Эти кнопки не для вас!', alert=True)
            return
        data = event.data.decode('utf-8')
        if data.startswith('help_page_'):
            return
        current_config = configparser.ConfigParser()
        current_config.read('config.ini', encoding='utf-8')
        if data == 'settings_general':
            text = '<b>⚙️ Общие настройки</b>\n\n'
            text += f"""📱 Устройство: <code>{current_config.get('Telegram', 'device_model', fallback='N/A')}</code>
"""
            text += f"""🖥 Система: <code>{current_config.get('Telegram', 'system_version', fallback='N/A')}</code>
"""
            text += f"""📝 Сессия: <code>{current_config.get('Telegram', 'session_name', fallback='N/A')}</code>
"""
            buttons = [[Button.inline('◀️ Назад', b'back_main')]]
            await event.edit(text, buttons=buttons)
        elif data == 'settings_prefix':
            current_prefix = current_config.get('Settings',
                'command_prefix', fallback='.')
            text = (
                f'<b>🔧 Префикс команд</b>\n\nТекущий префикс: <code>{current_prefix}</code>\n\n'
                )
            text += 'Для изменения префикса используйте команду:\n'
            text += (
                f'<code>{current_prefix}prefix &lt;новый_префикс&gt;</code>')
            buttons = [[Button.inline('◀️ Назад', b'back_main')]]
            await event.edit(text, buttons=buttons)
        elif data == 'settings_modules':
            text = '<b>📦 Управление модулями</b>\n\n'
            text += f'Загружено модулей: <b>{len(user_modules)}</b>\n\n'
            buttons = []
            for module_name, module_instance in user_modules.items():
                if hasattr(module_instance, 'CONFIG_HANDLER'
                    ) and module_instance.CONFIG_HANDLER:
                    icon = getattr(module_instance, 'CONFIG_ICON', '⚙️')
                    button_text = f'{icon} {module_instance.NAME}'
                    callback_data = f'module_{module_name}'.encode('utf-8')
                    buttons.append([Button.inline(button_text, callback_data)])
            buttons.append([Button.inline('◀️ Назад', b'back_main')])
            text += (
                'Выберите модуль для настройки или используйте команды:\n\n')
            text += f"""• <code>{current_config.get('Settings', 'command_prefix', fallback='.')}help</code> - список модулей
"""
            text += (
                f"• <code>{current_config.get('Settings', 'command_prefix', fallback='.')}lm &lt;файл&gt;</code> - загрузить модуль"
                )
            await event.edit(text, buttons=buttons)
        elif data.startswith('module_'):
            module_name = data.replace('module_', '')
            if module_name in user_modules:
                module_instance = user_modules[module_name]
                if hasattr(module_instance, 'CONFIG_HANDLER'
                    ) and module_instance.CONFIG_HANDLER:
                    await module_instance.CONFIG_HANDLER(event,
                        current_config, Button)
                else:
                    await event.answer('⚠️ У этого модуля нет настроек',
                        alert=True)
            else:
                await event.answer('❌ Модуль не найден', alert=True)
        elif data == 'settings_proxy':
            proxy_enabled = current_config.get('Proxy', 'enabled', fallback
                ='no') if current_config.has_section('Proxy') else 'no'
            text = '<b>🌐 Настройки прокси</b>\n\n'
            text += f"""Статус: {'✅ Включен' if proxy_enabled in ['yes', 'true', '1'] else '❌ Выключен'}

"""
            if proxy_enabled in ['yes', 'true', '1']:
                text += (
                    f"Тип: <code>{current_config.get('Proxy', 'type', fallback='N/A')}</code>\n"
                    )
                text += f"""Хост: <code>{current_config.get('Proxy', 'host', fallback='N/A')}</code>
"""
                text += f"""Порт: <code>{current_config.get('Proxy', 'port', fallback='N/A')}</code>
"""
            text += (
                '\nДля настройки отредактируйте файл <code>proxy.ini</code>')
            buttons = [[Button.inline('◀️ Назад', b'back_main')]]
            await event.edit(text, buttons=buttons)
        elif data == 'settings_info':
            text = '<b>ℹ️ Информация о Herikku</b>\n\n'
            text += '🤖 <b>Herikku Userbot</b>\n'
            text += 'Модульный Telegram юзербот\n\n'
            text += '📚 Возможности:\n'
            text += '• Модульная архитектура\n'
            text += '• Динамическая загрузка модулей\n'
            text += '• Inline-управление настройками\n'
            text += '• Поддержка прокси\n'
            text += '• Настраиваемый префикс\n'
            buttons = [[Button.inline('◀️ Назад', b'back_main')]]
            await event.edit(text, buttons=buttons)
        elif data == 'back_main':
            text = (
                '<b>⚙️ Меню настроек Herikku Userbot</b>\n\nВыберите раздел для настройки:'
                )
            buttons = [[Button.inline('⚙️ Общие настройки',
                b'settings_general')], [Button.inline('🔧 Префикс команд',
                b'settings_prefix')], [Button.inline('� Модули',
                b'settings_modules')], [Button.inline('🌐 Прокси',
                b'settings_proxy')], [Button.inline('ℹ️ Информация',
                b'settings_info')]]
            await event.edit(text, buttons=buttons)
        else:
            handled = False
            for module_name, module_instance in user_modules.items():
                if hasattr(module_instance, 'CONFIG_HANDLER'
                    ) and module_instance.CONFIG_HANDLER:
                    try:
                        await module_instance.CONFIG_HANDLER(event,
                            current_config, Button)
                        handled = True
                        break
                    except Exception as e:
                        continue
            if not handled:
                await event.answer('⚠️ Неизвестная команда', alert=True)
