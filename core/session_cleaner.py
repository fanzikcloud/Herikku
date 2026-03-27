import os
import glob
from telethon import TelegramClient
from telethon.errors import AuthKeyUnregisteredError, UserDeactivatedError, SessionPasswordNeededError
from core.text_formatter import TextFormatter


async def check_and_clean_sessions(api_id, api_hash, device_model,
    system_version, proxy=None, check_bots=True):
    print(TextFormatter.color('\n🔍 Проверка сессий...', 'cyan'))
    all_session_files = glob.glob('*.session')
    if not all_session_files:
        print(TextFormatter.color('ℹ️  Файлы сессий не найдены', 'cyan'))
        return [], [], [], []
    user_session_files = []
    bot_session_files = []
    for session_file in all_session_files:
        if session_file.startswith('inline_bot_session_'):
            bot_session_files.append(session_file)
        else:
            user_session_files.append(session_file)
    print(TextFormatter.color(
        f'📁 Найдено пользовательских сессий: {len(user_session_files)}',
        'cyan'))
    if check_bots and bot_session_files:
        print(TextFormatter.color(
            f'🤖 Найдено bot сессий: {len(bot_session_files)}', 'cyan'))
    active_sessions = []
    removed_sessions = []
    active_bots = []
    removed_bots = []
    print(TextFormatter.color('\n👤 Проверка пользовательских сессий:', 'cyan'))
    for session_file in user_session_files:
        session_name = session_file.replace('.session', '')
        print(TextFormatter.color(f'\n🔎 Проверка: {session_name}', 'yellow'))
        try:
            temp_client = TelegramClient(session_name, api_id, api_hash,
                device_model=device_model, system_version=system_version,
                proxy=proxy)
            await temp_client.connect()
            if await temp_client.is_user_authorized():
                try:
                    me = await temp_client.get_me()
                    username = (f'@{me.username}' if me.username else
                        'нет username')
                    print(TextFormatter.color(
                        f'✅ Активна: {me.first_name} ({username})', 'green'))
                    active_sessions.append({'file': session_file, 'name':
                        session_name, 'user': me.first_name, 'username':
                        username, 'id': me.id})
                except Exception as e:
                    print(TextFormatter.color(
                        f'⚠️  Ошибка получения данных: {e}', 'yellow'))
                    print(TextFormatter.color(
                        f'🗑️  Удаление неактивной сессии: {session_name}',
                        'red'))
                    await temp_client.disconnect()
                    os.remove(session_file)
                    removed_sessions.append(session_name)
            else:
                print(TextFormatter.color(
                    f'❌ Не авторизована: {session_name}', 'red'))
                print(TextFormatter.color(
                    f'🗑️  Удаление неактивной сессии: {session_name}', 'red'))
                await temp_client.disconnect()
                os.remove(session_file)
                removed_sessions.append(session_name)
            await temp_client.disconnect()
        except AuthKeyUnregisteredError:
            print(TextFormatter.color(
                f'❌ Ключ не зарегистрирован: {session_name}', 'red'))
            print(TextFormatter.color(
                f'🗑️  Удаление неактивной сессии: {session_name}', 'red'))
            os.remove(session_file)
            removed_sessions.append(session_name)
        except UserDeactivatedError:
            print(TextFormatter.color(
                f'❌ Пользователь деактивирован: {session_name}', 'red'))
            print(TextFormatter.color(
                f'🗑️  Удаление неактивной сессии: {session_name}', 'red'))
            os.remove(session_file)
            removed_sessions.append(session_name)
        except SessionPasswordNeededError:
            print(TextFormatter.color(
                f'⚠️  Требуется 2FA пароль: {session_name}', 'yellow'))
            print(TextFormatter.color(
                f'ℹ️  Сессия сохранена (требуется повторная авторизация)',
                'cyan'))
            active_sessions.append({'file': session_file, 'name':
                session_name, 'user': 'Требуется 2FA', 'username': '', 'id': 0}
                )
        except Exception as e:
            error_msg = str(e)
            print(TextFormatter.color(
                f'⚠️  Ошибка проверки {session_name}: {error_msg}', 'yellow'))
            if 'no such table' in error_msg.lower(
                ) or 'database' in error_msg.lower():
                print(TextFormatter.color(
                    f'❌ Поврежденная база данных сессии', 'red'))
                print(TextFormatter.color(
                    f'🗑️  Удаление поврежденной сессии: {session_name}', 'red')
                    )
                try:
                    os.remove(session_file)
                    journal_file = f'{session_file}-journal'
                    if os.path.exists(journal_file):
                        os.remove(journal_file)
                    removed_sessions.append(session_name)
                except Exception as remove_error:
                    print(TextFormatter.color(
                        f'⚠️  Не удалось удалить: {remove_error}', 'yellow'))
            else:
                print(TextFormatter.color(
                    f'ℹ️  Сессия сохранена (неизвестная ошибка)', 'cyan'))
    if check_bots and bot_session_files:
        print(TextFormatter.color('\n🤖 Проверка bot сессий:', 'cyan'))
        for session_file in bot_session_files:
            session_name = session_file.replace('.session', '')
            try:
                user_id = session_name.split('_')[-1]
                print(TextFormatter.color(
                    f'\n🔎 Проверка bot: {session_name} (user {user_id})',
                    'yellow'))
            except:
                print(TextFormatter.color(
                    f'\n🔎 Проверка bot: {session_name}', 'yellow'))
            try:
                temp_client = TelegramClient(session_name, api_id, api_hash,
                    device_model=device_model, system_version=
                    system_version, proxy=proxy)
                await temp_client.connect()
                if await temp_client.is_user_authorized():
                    try:
                        me = await temp_client.get_me()
                        bot_username = (f'@{me.username}' if me.username else
                            'нет username')
                        print(TextFormatter.color(
                            f'✅ Bot активен: {me.first_name} ({bot_username})',
                            'green'))
                        active_bots.append({'file': session_file, 'name':
                            session_name, 'bot': me.first_name, 'username':
                            bot_username, 'id': me.id})
                    except Exception as e:
                        print(TextFormatter.color(
                            f'⚠️  Ошибка получения данных bot: {e}', 'yellow'))
                        print(TextFormatter.color(
                            f'🗑️  Удаление неактивной bot сессии: {session_name}'
                            , 'red'))
                        await temp_client.disconnect()
                        os.remove(session_file)
                        removed_bots.append(session_name)
                else:
                    print(TextFormatter.color(
                        f'❌ Bot не авторизован: {session_name}', 'red'))
                    print(TextFormatter.color(
                        f'🗑️  Удаление неактивной bot сессии: {session_name}',
                        'red'))
                    await temp_client.disconnect()
                    os.remove(session_file)
                    removed_bots.append(session_name)
                await temp_client.disconnect()
            except AuthKeyUnregisteredError:
                print(TextFormatter.color(
                    f'❌ Bot ключ не зарегистрирован: {session_name}', 'red'))
                print(TextFormatter.color(
                    f'🗑️  Удаление неактивной bot сессии: {session_name}',
                    'red'))
                os.remove(session_file)
                removed_bots.append(session_name)
            except Exception as e:
                error_msg = str(e)
                print(TextFormatter.color(
                    f'⚠️  Ошибка проверки bot {session_name}: {error_msg}',
                    'yellow'))
                if 'no such table' in error_msg.lower(
                    ) or 'database' in error_msg.lower():
                    print(TextFormatter.color(
                        f'❌ Поврежденная база данных bot сессии', 'red'))
                    print(TextFormatter.color(
                        f'🗑️  Удаление поврежденной bot сессии: {session_name}'
                        , 'red'))
                    try:
                        os.remove(session_file)
                        journal_file = f'{session_file}-journal'
                        if os.path.exists(journal_file):
                            os.remove(journal_file)
                        removed_bots.append(session_name)
                    except Exception as remove_error:
                        print(TextFormatter.color(
                            f'⚠️  Не удалось удалить: {remove_error}',
                            'yellow'))
                else:
                    print(TextFormatter.color(
                        f'ℹ️  Bot сессия сохранена (неизвестная ошибка)',
                        'cyan'))
    print(TextFormatter.color('\n' + '=' * 50, 'cyan'))
    print(TextFormatter.color('📊 Результаты проверки:', 'cyan'))
    print(TextFormatter.color(
        f'✅ Активных пользовательских сессий: {len(active_sessions)}', 'green')
        )
    print(TextFormatter.color(
        f'🗑️  Удалено пользовательских сессий: {len(removed_sessions)}', 'red')
        )
    if check_bots:
        print(TextFormatter.color(
            f'🤖 Активных bot сессий: {len(active_bots)}', 'green'))
        print(TextFormatter.color(
            f'🗑️  Удалено bot сессий: {len(removed_bots)}', 'red'))
    print(TextFormatter.color('=' * 50 + '\n', 'cyan'))
    if active_sessions:
        print(TextFormatter.color('📋 Активные пользовательские сессии:',
            'green'))
        for session in active_sessions:
            if session['id'] != 0:
                print(TextFormatter.color(
                    f"  • {session['user']} ({session['username']}) - {session['name']}"
                    , 'green'))
            else:
                print(TextFormatter.color(
                    f"  • {session['user']} - {session['name']}", 'yellow'))
    if check_bots and active_bots:
        print(TextFormatter.color('\n🤖 Активные bot сессии:', 'green'))
        for bot in active_bots:
            print(TextFormatter.color(
                f"  • {bot['bot']} ({bot['username']}) - {bot['name']}",
                'green'))
    if removed_sessions:
        print(TextFormatter.color(
            '\n🗑️  Удаленные пользовательские сессии:', 'red'))
        for session in removed_sessions:
            print(TextFormatter.color(f'  • {session}', 'red'))
    if check_bots and removed_bots:
        print(TextFormatter.color('\n🗑️  Удаленные bot сессии:', 'red'))
        for bot in removed_bots:
            print(TextFormatter.color(f'  • {bot}', 'red'))
    return active_sessions, removed_sessions, active_bots, removed_bots


async def check_single_session(session_name, api_id, api_hash, device_model,
    system_version, proxy=None):
    try:
        temp_client = TelegramClient(session_name, api_id, api_hash,
            device_model=device_model, system_version=system_version, proxy
            =proxy)
        await temp_client.connect()
        if await temp_client.is_user_authorized():
            try:
                me = await temp_client.get_me()
                await temp_client.disconnect()
                return {'name': session_name, 'user': me.first_name,
                    'username': f'@{me.username}' if me.username else
                    'нет username', 'id': me.id, 'active': True}
            except Exception:
                await temp_client.disconnect()
                return None
        else:
            await temp_client.disconnect()
            return None
    except (AuthKeyUnregisteredError, UserDeactivatedError):
        return None
    except Exception:
        return None


def get_session_files(include_bots=False):
    all_sessions = glob.glob('*.session')
    if include_bots:
        return all_sessions
    else:
        return [f for f in all_sessions if not f.startswith(
            'inline_bot_session_')]


def remove_session(session_name):
    if not session_name.endswith('.session'):
        session_name += '.session'
    try:
        if os.path.exists(session_name):
            os.remove(session_name)
            return True
        return False
    except Exception as e:
        print(TextFormatter.color(f'❌ Ошибка удаления {session_name}: {e}',
            'red'))
        return False
