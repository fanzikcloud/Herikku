import configparser
import asyncio
from telethon import TelegramClient, events, Button
from core.text_formatter import TextFormatter
from core.config_manager import save_account_config

# Глобальный реестр для интерактивной настройки модулей через СМС.
# Хранит состояние ожидания ввода: {owner_id: {'action': 'edit_text', 'module': 'info', 'event': CallbackQuery.Event}}
userbot_pending_inputs = {}


async def start_account_bot(user_id, bot_token, api_id, api_hash, proxy,
    account_config, account_modules, account_bots, account_configs):
    try:
        bot_session_name = f'inline_bot_session_{user_id}'
        
        from core.proxy_manager import is_mtproto_proxy
        from telethon import connection
        proxy_kwargs = {}
        if proxy:
            if is_mtproto_proxy(proxy):
                proxy_kwargs['connection'] = connection.ConnectionTcpMTProxyRandomizedIntermediate
                proxy_kwargs['proxy'] = proxy
            else:
                proxy_kwargs['proxy'] = proxy

        bot_client = TelegramClient(bot_session_name, api_id, api_hash,
            **proxy_kwargs)
        await bot_client.start(bot_token=bot_token)
        from telethon.extensions import html
        bot_client.parse_mode = html
        
        # Убираем patched_edit у бота, так как inline-боты не должны переопределять edit_message, 
        # это ломает возвращаемые объекты callback-запросов и приводит к таймаутам!
        
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
            account_modules, account_configs)
        
        # Находим клиент юзербота для перехвата сообщений в любых чатах
        user_modules = account_modules.get(user_id, {})
        user_client = None
        for mod in user_modules.values():
            if hasattr(mod, 'client') and mod.client:
                user_client = mod.client
                break

        # Регистрируем обработчик перехвата исходящих СМС владельца в ЛЮБЫХ чатах
        if user_client:
            @user_client.on(events.NewMessage(outgoing=True))
            async def userbot_input_handler(user_event):
                if user_id in userbot_pending_inputs:
                    state = userbot_pending_inputs[user_id]
                    cb_event = state['event']
                    
                    # Проверяем, что сообщение отправлено в том же чате, где открыто меню настроек
                    if user_event.chat_id == cb_event.chat_id:
                        user_input = user_event.text.strip()
                        module = state['module']
                        
                        # Удаляем сообщение с новым шаблоном, чтобы не захламлять чат
                        try:
                            await user_event.delete()
                        except:
                            pass
                            
                        account_config = account_configs.get(user_id)
                        if account_config:
                            section_name = module.capitalize()
                            account_config.set(section_name, 'text', user_input)
                            save_account_config(user_id, account_configs)
                            
                            text = f"<b>✅ Шаблон модуля {section_name} успешно обновлен!</b>\n\n"
                            text += f"<i>Новое значение:</i>\n<code>{user_input}</code>"
                            buttons = [[Button.inline('◀️ К модулям', b'settings_modules')]]
                            try:
                                await cb_event.edit(text, buttons=buttons)
                            except Exception as edit_err:
                                print(f"Error editing callback event: {edit_err}")
                                
                        # Сбрасываем статус ожидания
                        del userbot_pending_inputs[user_id]

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


async def start_inline_bot_handler(bot, config, user_id, account_modules, account_configs):
    owner_id = user_id
    user_modules = account_modules.get(user_id, {})
    print(TextFormatter.color(f'🔒 Inline-бот защищен. Владелец: {owner_id}',
        'cyan'))

    @bot.on(events.NewMessage)
    async def private_message_handler(event):
        if not event.is_private:
            return
        if event.sender_id != owner_id:
            try:
                user = await event.get_sender()
                username = f'@{user.username}' if user.username else 'без username'
                user_name = user.first_name or 'Unknown'
                print(TextFormatter.color(
                    f'⚠️  Личное сообщение боту (аккаунт {user_id}): {user_name} ({username}, ID: {event.sender_id})'
                    , 'yellow'))
            except:
                pass
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
            except:
                await event.respond(text)
            return

        # Если сообщение от владельца в личке с ботом, и мы ждали ввода
        if event.sender_id in userbot_pending_inputs:
            state = userbot_pending_inputs[event.sender_id]
            if event.chat_id == state['event'].chat_id:
                action = state['action']
                module = state['module']
                user_input = event.text.strip()
                
                try:
                    await event.delete()
                except:
                    pass

                account_config = account_configs.get(user_id)
                if account_config:
                    section_name = module.capitalize()
                    account_config.set(section_name, 'text', user_input)
                    save_account_config(user_id, account_configs)
                    
                    text = f"<b>✅ Шаблон модуля {section_name} успешно обновлен!</b>\n\n"
                    text += f"<i>Новое значение:</i>\n<code>{user_input}</code>"
                    buttons = [[Button.inline('◀️ К модулям', b'settings_modules')]]
                    try:
                        await state['event'].edit(text, buttons=buttons)
                    except Exception as edit_err:
                        print(f"Error editing callback event: {edit_err}")
                        
                del userbot_pending_inputs[event.sender_id]

    @bot.on(events.InlineQuery)
    async def inline_handler(event):
        if event.sender_id != owner_id:
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
            except:
                result = builder.article(title=
                    '🤖 Herikku Userbot - Private', text=text, buttons=[[
                    Button.url('📦 Get Herikku',
                    'https://github.com/fanzikcloud/Herikku')]])
                await event.answer([result], cache_time=0)
            return

        query = event.text.strip().lower()
        if query.startswith('ttt_duel_') or query.startswith('rps_duel_') or query == 'info_inline':
            # Пропускаем специальные внутренние inline-запросы модулей, чтобы они не перебивались Control Panel
            return

        if query and query != 'config':
            return
        builder = event.builder
        
        prefix = config.get('Settings', 'command_prefix', fallback='.')
        
        text = '🤖 <b>Herikku Control Panel</b>\n'
        text += '═' * 30 + '\n\n'
        text += f'⚙️ <b>Префикс:</b> <code>{prefix}</code>\n'
        text += f'📦 <b>Модулей:</b> {len(user_modules)}\n\n'
        text += '<i>Выберите раздел для управления</i>'
        
        buttons = [
            [
                Button.inline('⚙️ Настройки', b'menu_settings'),
                Button.inline('📦 Модули', b'menu_modules')
            ],
            [
                Button.inline('📊 Статистика', b'menu_stats'),
                Button.inline('ℹ️ О боте', b'menu_info')
            ]
        ]
        
        result = builder.article(title='⚙️ Herikku Control Panel', text=text, buttons=buttons)
        await event.answer([result], cache_time=0)

    @bot.on(events.CallbackQuery)
    async def callback_handler(event):
        data = event.data.decode('utf-8')
        
        # Если кликнули по кастомной информационной кнопке Info или игровым кнопкам, разрешаем обработку всем
        if data == 'infobtn_alert' or data.startswith('ttt_') or data.startswith('rps_'):
            return
            
        if event.sender_id != owner_id:
            await event.answer('❌ Эти кнопки не для вас!', alert=True)
            return
        if data.startswith('help_page_'):
            return
            
        account_config = account_configs.get(user_id)
        if not account_config:
            return

        if data == 'back_main' or data == 'menu_main':
            prefix = account_config.get('Settings', 'command_prefix', fallback='.')
            
            text = '🤖 <b>Herikku Control Panel</b>\n'
            text += '═' * 30 + '\n\n'
            text += f'⚙️ <b>Префикс:</b> <code>{prefix}</code>\n'
            text += f'📦 <b>Модулей:</b> {len(user_modules)}\n\n'
            text += '<i>Выберите раздел для управления</i>'
            
            buttons = [
                [
                    Button.inline('⚙️ Настройки', b'menu_settings'),
                    Button.inline('📦 Модули', b'menu_modules')
                ],
                [
                    Button.inline('📊 Статистика', b'menu_stats'),
                    Button.inline('ℹ️ О боте', b'menu_info')
                ]
            ]
            await event.edit(text, buttons=buttons)
        
        elif data == 'menu_settings':
            text = '<b>⚙️ Настройки</b>\n'
            text += '─' * 30 + '\n\n'
            text += '<i>Управление параметрами юзербота</i>'
            
            buttons = [
                [Button.inline('🔧 Префикс команд', b'settings_prefix')],
                [Button.inline('🌐 Прокси', b'settings_proxy')],
                [Button.inline('🖥️ Система', b'settings_system')],
                [Button.inline('◀️ Главное меню', b'back_main')]
            ]
            await event.edit(text, buttons=buttons)
        
        elif data == 'menu_modules' or data == 'settings_modules':
            text = '<b>📦 Управление модулями</b>\n'
            text += '─' * 30 + '\n\n'
            text += f'<b>Загружено:</b> {len(user_modules)} модулей\n\n'
            
            buttons = []
            configurable_modules = []
            for module_name, module_instance in user_modules.items():
                if hasattr(module_instance, 'CONFIG_HANDLER') and module_instance.CONFIG_HANDLER:
                    icon = getattr(module_instance, 'CONFIG_ICON', '⚙️')
                    configurable_modules.append((module_name, module_instance, icon))
            
            if configurable_modules:
                text += '<i>Выберите модуль для настройки через кнопки:</i>\n'
                row = []
                for module_name, module_instance, icon in configurable_modules:
                    button_text = f'{icon} {module_instance.NAME}'
                    callback_data = f'module_{module_name}'.encode('utf-8')
                    row.append(Button.inline(button_text, callback_data))
                    if len(row) == 2:
                        buttons.append(row)
                        row = []
                if row:
                    buttons.append(row)
            else:
                text += '<i>Нет модулей с настройками</i>\n'
            
            prefix = account_config.get('Settings', 'command_prefix', fallback='.')
            text += f'\n<b>Команды:</b>\n'
            text += f'• <code>{prefix}help</code> - список модулей\n'
            text += f'• <code>{prefix}lm</code> - загрузить модуль\n'
            text += f'• <code>{prefix}um</code> - выгрузить модуль'
            
            buttons.append([Button.inline('◀️ Главное меню', b'back_main')])
            await event.edit(text, buttons=buttons)
        
        elif data == 'menu_stats':
            import psutil
            
            text = '<b>📊 Статистика</b>\n'
            text += '─' * 30 + '\n\n'
            
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                text += f'💻 <b>CPU:</b> {cpu_percent}%\n'
            except:
                pass
            
            try:
                memory = psutil.virtual_memory()
                text += f'🧠 <b>RAM:</b> {memory.percent}%\n'
            except:
                pass
            
            text += f'📦 <b>Модулей:</b> {len(user_modules)}\n'
            
            buttons = [[Button.inline('◀️ Главное меню', b'back_main')]]
            await event.edit(text, buttons=buttons)
        
        elif data == 'menu_info' or data == 'settings_info':
            text = '<b>ℹ️ О Herikku Userbot</b>\n'
            text += '─' * 30 + '\n\n'
            text += '<b>Herikku</b> - модульный Telegram юзербот\n\n'
            text += '🚀 <b>Возможности:</b>\n'
            text += '• Модульная архитектура\n'
            text += '• Динамическая загрузка модулей\n'
            text += '• Inline-управление\n'
            text += '• Система прав доступа\n'
            text += '• Поддержка тем\n'
            text += '• Мультиаккаунт\n\n'
            text += '📚 GitHub: <a href="https://github.com/fanzikcloud/Herikku">fanzikcloud/Herikku</a>'
            
            buttons = [
                [Button.url('📦 GitHub', 'https://github.com/fanzikcloud/Herikku')],
                [Button.inline('◀️ Главное меню', b'back_main')]
            ]
            await event.edit(text, buttons=buttons)
        
        elif data == 'settings_prefix':
            current_prefix = account_config.get('Settings', 'command_prefix', fallback='.')
            
            text = '<b>🔧 Префикс команд</b>\n'
            text += '─' * 30 + '\n\n'
            text += f'⚙️ <b>Текущий префикс:</b> <code>{current_prefix}</code>\n\n'
            text += '<b>Изменение префикса:</b>\n'
            text += f'<code>{current_prefix}prefix &lt;новый_префикс&gt;</code>\n\n'
            text += '<i>Примеры:</i> <code>.</code> <code>!</code> <code>/</code> <code>-</code>'
            
            buttons = [[Button.inline('◀️ Настройки', b'menu_settings')]]
            await event.edit(text, buttons=buttons)
        
        elif data == 'settings_proxy':
            proxy_enabled = account_config.get('Proxy', 'enabled', fallback='no') if account_config.has_section('Proxy') else 'no'
            enabled = proxy_enabled in ['yes', 'true', '1']
            
            text = '<b>🌐 Настройки прокси</b>\n'
            text += '─' * 30 + '\n\n'
            status_emoji = '✅' if enabled else '❌'
            text += f'{status_emoji} <b>Статус:</b> {"Включен" if enabled else "Выключен"}\n\n'
            
            if enabled:
                proxy_type = account_config.get('Proxy', 'type', fallback='N/A')
                host = account_config.get('Proxy', 'host', fallback='N/A')
                port = account_config.get('Proxy', 'port', fallback='N/A')
                text += f'📡 <b>Тип:</b> <code>{proxy_type}</code>\n'
                text += f'🌍 <b>Хост:</b> <code>{host}</code>\n'
                text += f'🔌 <b>Порт:</b> <code>{port}</code>\n'
            
            text += '\n<i>Для настройки отредактируйте файл</i> <code>proxy.ini</code>'
            buttons = [[Button.inline('◀️ Настройки', b'menu_settings')]]
            await event.edit(text, buttons=buttons)
        
        elif data == 'settings_system':
            import sys
            
            text = '<b>🖥️ Системная информация</b>\n'
            text += '─' * 30 + '\n\n'
            
            device = account_config.get('Telegram', 'device_model', fallback='N/A')
            system = account_config.get('Telegram', 'system_version', fallback='N/A')
            session = account_config.get('Telegram', 'session_name', fallback='N/A')
            
            text += f'📱 <b>Устройство:</b> <code>{device}</code>\n'
            text += f'🖥️ <b>Система:</b> <code>{system}</code>\n'
            text += f'📝 <b>Сессия:</b> <code>{session}</code>\n'
            text += f'🐍 <b>Python:</b> <code>{sys.version.split()[0]}</code>\n'
            
            buttons = [[Button.inline('◀️ Настройки', b'menu_settings')]]
            await event.edit(text, buttons=buttons)

        # Обработка кликов по модулям
        elif data.startswith('module_'):
            module_name = data.replace('module_', '')
            if module_name in user_modules:
                module_instance = user_modules[module_name]
                if hasattr(module_instance, 'CONFIG_HANDLER') and module_instance.CONFIG_HANDLER:
                    # Добавляем интерактивные кнопки быстрого изменения текста для Info, Ping, Help
                    if module_name in ['info', 'ping', 'help']:
                        section_name = module_name.capitalize()
                        current_text = account_config.get(section_name, 'text', fallback='')
                        if not current_text and module_name == 'help':
                            current_text = 'не установлен (дефолт)'
                        
                        text = f'<b>👤 Настройка модуля {section_name}</b>\n'
                        text += '─' * 30 + '\n\n'
                        text += f'📝 <b>Текущий шаблон:</b>\n<code>{current_text[:200]}</code>\n\n'
                        text += '<i>Нажмите кнопку ниже, чтобы изменить текст, отправив его следующим сообщением прямо в этот же чат.</i>'
                        
                        buttons = [
                            [Button.inline('✏️ Изменить текст шаблона', f'edit_text_{module_name}'.encode('utf-8'))],
                            [Button.inline('◀️ К модулям', b'settings_modules')]
                        ]
                        await event.edit(text, buttons=buttons)
                    else:
                        await module_instance.CONFIG_HANDLER(event, account_config, Button)
                else:
                    await event.answer('⚠️ У этого модуля нет настроек', alert=True)
            else:
                await event.answer('❌ Модуль не найден', alert=True)

        # Включение режима ожидания ввода от пользователя
        elif data.startswith('edit_text_'):
            module_name = data.replace('edit_text_', '')
            userbot_pending_inputs[event.sender_id] = {
                'action': 'edit_text',
                'module': module_name,
                'event': event # Сохраняем event кнопки
            }
            # Отвечаем алертом, что ждем ввода
            await event.answer('✏️ Отправьте новый текст шаблона в этот чат!', alert=True)
            
            text = f'<b>✏️ Ожидание ввода для модуля {module_name.capitalize()}</b>\n'
            text += '─' * 30 + '\n\n'
            text += '<b>Шаг 1:</b> Просто напишите новый текст шаблона в этот же чат (можно использовать любые плейсхолдеры и Markdown).\n'
            text += '<b>Шаг 2:</b> Отправьте сообщение. Бот автоматически применит настройки!\n\n'
            text += '<i>Для отмены нажмите кнопку Назад.</i>'
            
            buttons = [[Button.inline('◀️ Отмена', b'settings_modules')]]
            await event.edit(text, buttons=buttons)

        elif data == 'infobtn_alert':
            # Это кастомный клик по кнопке Info, мы пропускаем его, так как его обрабатывает сам модуль Info в INLINE_HANDLERS
            return

        else:
            handled = False
            for module_name, module_instance in user_modules.items():
                if hasattr(module_instance, 'CONFIG_HANDLER') and module_instance.CONFIG_HANDLER:
                    try:
                        await module_instance.CONFIG_HANDLER(event, account_config, Button)
                        handled = True
                        break
                    except Exception:
                        continue
            if not handled:
                await event.answer('⚠️ Неизвестная команда', alert=True)
