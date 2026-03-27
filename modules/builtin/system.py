from core.base_module import Module
import os
import sys
import asyncio
import glob
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


class SystemModule(Module):
    NAME = 'System'
    AUTHOR = 'Herikku'
    DESCRIPTION = (
        'Системные команды: перезагрузка, самоуничтожение и мульти-аккаунт')
    DEPENDENCIES = []
    COMMANDS = {'restart': 'Перезагрузить бота', 'die':
        'Выйти из аккаунта и удалить сессию', 'addaccount':
        'Добавить дополнительный аккаунт', 'listaccounts':
        'Список подключенных аккаунтов', 'checkaccounts':
        'Проверить статус всех аккаунтов', 'cleansessions':
        'Проверить и удалить неактивные сессии'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.loaded_modules = loaded_modules
        self.events = events
        self.load_module = load_module
        self.config_path = config_path
        self.install_package = install_package
        self.bot_start_time = bot_start_time
        self.add_client_callback = None

        async def restart_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}restart'):
                return
            await event.edit('🔄 Перезагрузка бота...')
            await asyncio.sleep(1)
            os.execl(sys.executable, sys.executable, *sys.argv)

        async def die_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}die'
                ):
                return
            await event.edit(
                '💀 Самоуничтожение активировано...\n\n⚠️ Сессия будет удалена!'
                )
            session_name = self.config.get('Telegram', 'session_name',
                fallback='herikku_session')
            session_file = f'{session_name}.session'
            await client.log_out()
            if os.path.exists(session_file):
                os.remove(session_file)
            sys.exit(0)

        async def addaccount_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}addaccount'):
                return
            await event.edit(
                """**📱 Добавление нового аккаунта**

⏳ Начинаю процесс авторизации..."""
                )
            try:
                api_id = self.config.getint('Telegram', 'api_id')
                api_hash = self.config.get('Telegram', 'api_hash')
                device_model = self.config.get('Telegram', 'device_model',
                    fallback='Herikku')
                system_version = self.config.get('Telegram',
                    'system_version', fallback='1.0')
                import time
                session_name = f'herikku_account_{int(time.time())}'
                session_file = f'{session_name}.session'
                await event.edit(
                    """**📱 Добавление нового аккаунта**

📞 Введите номер телефона в формате: +1234567890

⚠️ Отправьте номер в ответ на это сообщение"""
                    )
                auth_data = {'phone': None, 'client': None, 'step': 'phone',
                    'session_name': session_name, 'session_file': session_file}

                def cleanup_session():
                    try:
                        if os.path.exists(auth_data['session_file']):
                            os.remove(auth_data['session_file'])
                            print(
                                f"� Удалена неудачная сессия: {auth_data['session_file']}"
                                )
                    except Exception as e:
                        print(f'⚠️ Не удалось удалить сессию: {e}')

                async def auth_step_handler(step_event):
                    if (not step_event.is_reply or step_event.
                        reply_to_msg_id != event.id):
                        return
                    user_input = step_event.text.strip()
                    await step_event.delete()
                    try:
                        if auth_data['step'] == 'phone':
                            auth_data['phone'] = user_input
                            await event.edit(
                                f"""**📱 Добавление нового аккаунта**

📞 Номер: <code>{user_input}</code>
⏳ Подключение..."""
                                )
                            new_client = TelegramClient(session_name,
                                api_id, api_hash, device_model=device_model,
                                system_version=system_version)
                            auth_data['client'] = new_client
                            await new_client.connect()
                            if await new_client.is_user_authorized():
                                me = await new_client.get_me()
                                if self.add_client_callback:
                                    self.add_client_callback(new_client)
                                await event.edit(
                                    f"""**📱 Аккаунт уже авторизован!**

✅ Подключен как:
� {me.first_name}
🆔 ID: <code>{me.id}</code>
📱 @{me.username if me.username else 'нет username'}

💾 Сессия: <code>{session_name}.session</code>"""
                                    )
                                client.remove_event_handler(auth_step_handler)
                                return
                            await event.edit(
                                f"""**📱 Добавление нового аккаунта**

📞 Номер: <code>{auth_data['phone']}</code>
⏳ Отправляю код..."""
                                )
                            await new_client.send_code_request(auth_data[
                                'phone'])
                            auth_data['step'] = 'code'
                            await event.edit(
                                f"""**📱 Добавление нового аккаунта**

📞 Номер: <code>{auth_data['phone']}</code>
✅ Код отправлен!

🔢 Введите код из Telegram (5 цифр без пробелов)

⚠️ Отправьте код в ответ на это сообщение"""
                                )
                        elif auth_data['step'] == 'code':
                            code = user_input.replace(' ', '').replace('-', '')
                            await event.edit(
                                f"""**📱 Добавление нового аккаунта**

📞 Номер: <code>{auth_data['phone']}</code>
🔢 Код: <code>{code}</code>
⏳ Авторизация..."""
                                )
                            try:
                                await auth_data['client'].sign_in(auth_data
                                    ['phone'], code)
                                me = await auth_data['client'].get_me()
                                if self.add_client_callback:
                                    self.add_client_callback(auth_data[
                                        'client'])
                                await event.edit(
                                    f"""**📱 Аккаунт добавлен!**

✅ Успешно авторизован как:
👤 {me.first_name}
🆔 ID: <code>{me.id}</code>
📱 @{me.username if me.username else 'нет username'}

💾 Сессия: <code>{session_name}.session</code>

🔧 Все команды юзербота теперь работают на этом аккаунте!
⏳ Модули загружаются в фоне..."""
                                    )
                                client.remove_event_handler(auth_step_handler)
                            except SessionPasswordNeededError:
                                auth_data['step'] = 'password'
                                await event.edit(
                                    f"""**📱 Добавление нового аккаунта**

📞 Номер: <code>{auth_data['phone']}</code>
🔐 Требуется 2FA пароль

⚠️ Введите пароль двухфакторной аутентификации в ответ на это сообщение"""
                                    )
                            except Exception as code_error:
                                error_msg = str(code_error)
                                await event.edit(
                                    f"""**📱 Ошибка авторизации**

❌ {error_msg}

💡 Проверьте правильность кода и попробуйте снова с команды .addaccount"""
                                    )
                                if auth_data['client']:
                                    await auth_data['client'].disconnect()
                                cleanup_session()
                                client.remove_event_handler(auth_step_handler)
                        elif auth_data['step'] == 'password':
                            password = user_input
                            await event.edit(
                                f"""**📱 Добавление нового аккаунта**

📞 Номер: <code>{auth_data['phone']}</code>
🔐 Проверка пароля..."""
                                )
                            try:
                                await auth_data['client'].sign_in(password=
                                    password)
                                me = await auth_data['client'].get_me()
                                if self.add_client_callback:
                                    self.add_client_callback(auth_data[
                                        'client'])
                                await event.edit(
                                    f"""**📱 Аккаунт добавлен!**

✅ Успешно авторизован как:
👤 {me.first_name}
🆔 ID: <code>{me.id}</code>
📱 @{me.username if me.username else 'нет username'}

💾 Сессия: <code>{session_name}.session</code>

🔧 Все команды юзербота теперь работают на этом аккаунте!
⏳ Модули загружаются в фоне..."""
                                    )
                                client.remove_event_handler(auth_step_handler)
                            except Exception as pwd_error:
                                await event.edit(
                                    f"""**📱 Ошибка авторизации**

❌ Неверный пароль 2FA:
<code>{str(pwd_error)}</code>

💡 Попробуйте снова с команды .addaccount"""
                                    )
                                if auth_data['client']:
                                    await auth_data['client'].disconnect()
                                cleanup_session()
                                client.remove_event_handler(auth_step_handler)
                    except Exception as step_error:
                        await event.edit(f'**📱 Ошибка**\n\n❌ {str(step_error)}'
                            )
                        if auth_data.get('client'):
                            try:
                                await auth_data['client'].disconnect()
                            except:
                                pass
                        cleanup_session()
                        client.remove_event_handler(auth_step_handler)
                client.add_event_handler(auth_step_handler, events.
                    NewMessage(outgoing=True))
            except Exception as e:
                await event.edit(
                    f"""**📱 Ошибка**

❌ Не удалось начать процесс:
<code>{str(e)}</code>"""
                    )

        async def listaccounts_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}listaccounts'):
                return
            session_files = glob.glob('herikku_account_*.session') + glob.glob(
                'herriku_account_*.session')
            session_files = list(set(session_files))
            message = '**📱 Подключенные аккаунты:**\n\n'
            me = await client.get_me()
            main_session = self.config.get('Telegram', 'session_name',
                fallback='herikku_session')
            message += f'👤 <b>Основной:</b> {me.first_name}\n'
            message += f'   🆔 ID: <code>{me.id}</code>\n'
            message += (
                f"   📱 @{me.username if me.username else 'нет username'}\n")
            message += f'   💾 <code>{main_session}.session</code>\n\n'
            if len(session_files) > 0:
                message += f'<b>Дополнительные ({len(session_files)}):</b>\n'
                for session_file in session_files:
                    session_name = session_file.replace('.session', '')
                    message += f'   💾 <code>{session_name}</code>\n'
            else:
                message += '<i>Дополнительные аккаунты не найдены</i>'
            await event.edit(message)

        async def checkaccounts_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}checkaccounts'):
                return
            from core.progress_bar import SpinnerProgress
            msg = await event.edit('🔍 Проверка аккаунтов...')
            spinner = SpinnerProgress(msg, 'Проверка аккаунтов...')
            await spinner.start()
            try:
                api_id = self.config.getint('Telegram', 'api_id')
                api_hash = self.config.get('Telegram', 'api_hash')
                device_model = self.config.get('Telegram', 'device_model',
                    fallback='Herikku')
                system_version = self.config.get('Telegram',
                    'system_version', fallback='1.0')
                accounts_info = []
                me = await client.get_me()
                main_session = self.config.get('Telegram', 'session_name',
                    fallback='herikku_session')
                premium_emoji = '⭐' if me.premium else ''
                accounts_info.append({'type': 'main', 'name': me.first_name,
                    'username': me.username, 'id': me.id, 'session':
                    main_session, 'status': 'online', 'premium': me.premium,
                    'phone': me.phone if hasattr(me, 'phone') else None})
                session_files = glob.glob('herikku_account_*.session'
                    ) + glob.glob('herriku_account_*.session')
                session_files = list(set(session_files))
                for session_file in session_files:
                    session_name = session_file.replace('.session', '')
                    try:
                        test_client = TelegramClient(session_name, api_id,
                            api_hash, device_model=device_model,
                            system_version=system_version)
                        await test_client.connect()
                        if await test_client.is_user_authorized():
                            acc_me = await test_client.get_me()
                            accounts_info.append({'type': 'additional',
                                'name': acc_me.first_name, 'username':
                                acc_me.username, 'id': acc_me.id, 'session':
                                session_name, 'status': 'online', 'premium':
                                acc_me.premium, 'phone': acc_me.phone if
                                hasattr(acc_me, 'phone') else None})
                        else:
                            accounts_info.append({'type': 'additional',
                                'session': session_name, 'status':
                                'unauthorized'})
                        await test_client.disconnect()
                    except Exception as e:
                        accounts_info.append({'type': 'additional',
                            'session': session_name, 'status': 'error',
                            'error': str(e)})
                await spinner.stop()
                message = '**📊 Статус аккаунтов:**\n\n'
                for acc in accounts_info:
                    if acc['type'] == 'main':
                        premium_badge = ' ⭐' if acc.get('premium') else ''
                        message += (
                            f'👤 <b>Основной аккаунт{premium_badge}</b>\n')
                        message += f'   ✅ Статус: <b>Онлайн</b>\n'
                        message += f"   📝 Имя: {acc['name']}\n"
                        message += f"   🆔 ID: <code>{acc['id']}</code>\n"
                        if acc['username']:
                            message += f"   📱 Username: @{acc['username']}\n"
                        if acc.get('phone'):
                            message += (
                                f"   📞 Телефон: <code>{acc['phone']}</code>\n")
                        if acc.get('premium'):
                            message += f'   ⭐ Premium: <b>Да</b>\n'
                        message += (
                            f"   💾 Сессия: <code>{acc['session']}</code>\n\n")
                additional_accounts = [acc for acc in accounts_info if acc[
                    'type'] == 'additional']
                if additional_accounts:
                    message += (
                        f'<b>Дополнительные аккаунты ({len(additional_accounts)}):</b>\n\n'
                        )
                    for i, acc in enumerate(additional_accounts, 1):
                        if acc['status'] == 'online':
                            premium_badge = ' ⭐' if acc.get('premium') else ''
                            message += (
                                f"{i}. <b>{acc['name']}{premium_badge}</b>\n")
                            message += f'   ✅ Статус: <b>Онлайн</b>\n'
                            message += f"   🆔 ID: <code>{acc['id']}</code>\n"
                            if acc['username']:
                                message += f"   📱 @{acc['username']}\n"
                            if acc.get('premium'):
                                message += f'   ⭐ Premium: <b>Да</b>\n'
                            message += (
                                f"   💾 <code>{acc['session']}</code>\n\n")
                        elif acc['status'] == 'unauthorized':
                            message += f'{i}. ⚠️ <b>Не авторизован</b>\n'
                            message += f"   💾 <code>{acc['session']}</code>\n"
                            message += (
                                f'   💡 Требуется повторная авторизация\n\n')
                        elif acc['status'] == 'error':
                            message += f'{i}. ❌ <b>Ошибка</b>\n'
                            message += f"   💾 <code>{acc['session']}</code>\n"
                            message += (
                                f"   ⚠️ {acc.get('error', 'Неизвестная ошибка')}\n\n"
                                )
                else:
                    message += '<i>Дополнительные аккаунты не найдены</i>\n\n'
                online_count = sum(1 for acc in accounts_info if acc[
                    'status'] == 'online')
                premium_count = sum(1 for acc in accounts_info if acc.get(
                    'premium'))
                message += f'📊 <b>Итого:</b>\n'
                message += f'   • Всего аккаунтов: {len(accounts_info)}\n'
                message += f'   • Онлайн: {online_count}\n'
                if premium_count > 0:
                    message += f'   • Premium: {premium_count} ⭐\n'
                await msg.edit(message)
            except Exception as e:
                await spinner.stop()
                await msg.edit(
                    f'❌ Ошибка проверки аккаунтов:\n<code>{str(e)}</code>')
                import traceback
                traceback.print_exc()

        async def cleansessions_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}cleansessions'):
                return
            from core.session_cleaner import check_and_clean_sessions, get_session_files
            from core.proxy_manager import load_proxy
            session_files_before = get_session_files(include_bots=True)
            if not session_files_before:
                await event.edit(
                    '<b>ℹ️ Файлы сессий не найдены</b>\n\nНечего проверять!')
                return
            await event.edit(
                f"""<b>🔍 Проверка сессий...</b>

Найдено файлов: <code>{len(session_files_before)}</code>
⏳ Это может занять некоторое время...

<i>⚠️ Активные сессии могут вызвать ошибку "database is locked"</i>"""
                )
            try:
                api_id = self.config.getint('Telegram', 'api_id')
                api_hash = self.config.get('Telegram', 'api_hash')
                device_model = self.config.get('Telegram', 'device_model',
                    fallback='Herikku')
                system_version = self.config.get('Telegram',
                    'system_version', fallback='1.0')
                proxy = load_proxy()
                (active_sessions, removed_sessions, active_bots, removed_bots
                    ) = (await check_and_clean_sessions(api_id, api_hash,
                    device_model, system_version, proxy, check_bots=True))
                total_active = len(active_sessions) + len(active_bots)
                total_removed = len(removed_sessions) + len(removed_bots)
                message = '<b>🧹 Очистка сессий завершена!</b>\n\n'
                message += f'✅ Активных: <b>{total_active}</b>\n'
                if active_sessions:
                    message += (
                        f'  • Пользовательских: <b>{len(active_sessions)}</b>\n'
                        )
                if active_bots:
                    message += f'  • Bot сессий: <b>{len(active_bots)}</b>\n'
                message += f'\n🗑 Удалено: <b>{total_removed}</b>\n'
                if removed_sessions:
                    message += (
                        f'  • Пользовательских: <b>{len(removed_sessions)}</b>\n'
                        )
                if removed_bots:
                    message += f'  • Bot сессий: <b>{len(removed_bots)}</b>\n'
                message += '\n'
                if active_sessions:
                    message += '<b>📋 Активные пользовательские сессии:</b>\n'
                    for session in active_sessions:
                        if session['id'] != 0:
                            message += (
                                f"• {session['user']} ({session['username']})\n"
                                )
                            message += f"  💾 <code>{session['name']}</code>\n"
                        else:
                            message += f"• {session['user']}\n"
                            message += f"  💾 <code>{session['name']}</code>\n"
                    message += '\n'
                if active_bots:
                    message += '<b>🤖 Активные bot сессии:</b>\n'
                    for bot in active_bots:
                        message += f"• {bot['bot']} ({bot['username']})\n"
                        message += f"  💾 <code>{bot['name']}</code>\n"
                    message += '\n'
                if removed_sessions:
                    message += '<b>🗑 Удаленные пользовательские сессии:</b>\n'
                    for session in removed_sessions:
                        message += f'• <code>{session}</code>\n'
                    message += '\n'
                if removed_bots:
                    message += '<b>🗑 Удаленные bot сессии:</b>\n'
                    for bot in removed_bots:
                        message += f'• <code>{bot}</code>\n'
                    message += '\n'
                if total_removed > 0:
                    message += '✨ <i>Освобождено место на диске!</i>'
                else:
                    message += '✨ <i>Все сессии активны!</i>'
                await event.edit(message)
            except Exception as e:
                await event.edit(
                    f"""<b>❌ Ошибка при проверке сессий:</b>

<code>{str(e)}</code>

<i>Попробуйте запустить clean_sessions.py вручную</i>"""
                    )
        client.add_event_handler(restart_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(die_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(addaccount_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(listaccounts_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(checkaccounts_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(cleansessions_handler, events.NewMessage(
            outgoing=True))
