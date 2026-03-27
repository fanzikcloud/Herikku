import os
import sys
sys.dont_write_bytecode = True
import asyncio
import glob
from datetime import datetime
from telethon import TelegramClient
from core.banner import print_banner
from core.text_formatter import TextFormatter
from core.config_manager import load_config, get_account_config, save_account_config
from core.proxy_manager import load_proxy
from core.module_loader import load_builtin_modules
from core.inline_bot import start_account_bot
loaded_modules = {}
account_modules = {}
bot_start_time = datetime.now()
additional_clients = []
account_configs = {}
account_bots = {}


def add_additional_client(new_client):
    global additional_clients
    additional_clients.append(new_client)
    print(TextFormatter.color(
        f'✅ Дополнительный клиент добавлен. Всего клиентов: {len(additional_clients) + 1}'
        , 'green'))


async def setup_account(client, api_id, api_hash, device_model,
    system_version, proxy, command_prefix, is_main=False):
    me = await client.get_me()
    user_id = me.id
    config = get_account_config(user_id, account_configs)
    bot_token = config.get('InlineBot', 'token', fallback='').strip()
    if not bot_token:
        print(TextFormatter.color(
            f'🤖 Настройка inline-бота для аккаунта {me.first_name}...', 'cyan')
            )
        from core.bot_creator import create_bot_via_botfather
        bot_data = await create_bot_via_botfather(client)
        if bot_data:
            bot_token = bot_data['token']
            config.set('InlineBot', 'token', bot_token)
            config.set('InlineBot', 'username', bot_data['username'])
            config.set('InlineBot', 'name', bot_data['name'])
            save_account_config(user_id, account_configs)
            print(TextFormatter.color(
                f"✅ Бот создан для {me.first_name}: @{bot_data['username']}",
                'green'))
    print(TextFormatter.color(f'📦 Загрузка модулей для {me.first_name}...',
        'cyan'))
    await load_builtin_modules(client, command_prefix, config, user_id,
        account_modules, loaded_modules, bot_start_time, 
        add_additional_client if is_main else None)
    if bot_token:
        await start_account_bot(user_id, bot_token, api_id, api_hash, proxy,
            config, account_modules, account_bots, account_configs)
    return user_id


async def load_additional_accounts(api_id, api_hash, device_model,
    system_version, proxy, command_prefix):
    session_files = glob.glob('herikku_account_*.session') + glob.glob(
        'herriku_account_*.session')
    session_files = list(set(session_files))
    typo_files = [f for f in session_files if f.startswith('herriku_')]
    if typo_files:
        print(TextFormatter.color(
            f'⚠️  Найдены файлы с опечаткой в имени (herriku вместо herikku): {len(typo_files)}'
            , 'yellow'))
        print(TextFormatter.color(
            f'💡 Рекомендуется переименовать их для единообразия', 'cyan'))
    if session_files:
        print(TextFormatter.color(
            f'📱 Найдено дополнительных аккаунтов: {len(session_files)}',
            'green'))
        for session_file in session_files:
            session_name_only = session_file.replace('.session', '')
            try:
                add_client = TelegramClient(session_name_only, api_id,
                    api_hash, device_model=device_model, system_version=
                    system_version, proxy=proxy)
                from telethon.extensions import html
                add_client.parse_mode = html
                from core.formatting import markdown_to_html
                original_edit = add_client.edit_message

                async def patched_edit(*args, **kwargs):
                    args_list = list(args)
                    if len(args_list) >= 2:
                        if isinstance(args_list[1], str):
                            args_list[1] = markdown_to_html(args_list[1])
                        elif len(args_list) >= 3 and isinstance(args_list[2
                            ], str):
                            args_list[2] = markdown_to_html(args_list[2])
                    if 'message' in kwargs and isinstance(kwargs['message'],
                        str):
                        kwargs['message'] = markdown_to_html(kwargs['message'])
                    if 'text' in kwargs and isinstance(kwargs['text'], str):
                        kwargs['text'] = markdown_to_html(kwargs['text'])
                    return await original_edit(*args_list, **kwargs)
                add_client.edit_message = patched_edit
                await add_client.connect()
                if await add_client.is_user_authorized():
                    add_me = await add_client.get_me()
                    print(TextFormatter.color(
                        f"✅ Подключен: {add_me.first_name} (@{add_me.username if add_me.username else 'нет username'})"
                        , 'green'))
                    additional_clients.append(add_client)
                else:
                    print(TextFormatter.color(
                        f'⚠️  Сессия {session_name_only} не авторизована, пропускаю'
                        , 'yellow'))
                    await add_client.disconnect()
            except Exception as e:
                print(TextFormatter.color(
                    f'⚠️  Ошибка загрузки {session_file}: {e}', 'yellow'))
    else:
        print(TextFormatter.color('ℹ️  Дополнительные аккаунты не найдены',
            'cyan'))


async def update_bot_commands(api_id, api_hash, device_model,
    system_version, proxy, command_prefix, main_user_id, main_client):
    for user_id, bot in account_bots.items():
        try:
            account_config = account_configs.get(user_id)
            if account_config:
                bot_username = account_config.get('InlineBot', 'username',
                    fallback='')
                if bot_username:
                    from core.bot_creator import update_bot_commands_from_modules
                    if user_id == main_user_id:
                        user_client = main_client
                    else:
                        user_client = None
                        for add_client in additional_clients:
                            add_me = await add_client.get_me()
                            if add_me.id == user_id:
                                user_client = add_client
                                break
                    if user_client:
                        user_modules = account_modules.get(user_id, {})
                        await update_bot_commands_from_modules(user_client,
                            bot_username, user_modules, command_prefix)
        except Exception as e:
            print(TextFormatter.color(
                f'⚠️ Ошибка обновления команд бота для аккаунта {user_id}: {e}'
                , 'yellow'))


async def monitor_additional_clients(api_id, api_hash, device_model,
    system_version, proxy, command_prefix):
    processed_clients = set(additional_clients)
    running_tasks = []
    while True:
        for new_client in additional_clients:
            if new_client not in processed_clients:
                print(TextFormatter.color(
                    f'🔄 Загрузка модулей для нового клиента...', 'cyan'))
                await setup_account(new_client, api_id, api_hash,
                    device_model, system_version, proxy, command_prefix,
                    is_main=False)
                processed_clients.add(new_client)
                task = asyncio.create_task(new_client.run_until_disconnected())
                running_tasks.append(task)
                print(TextFormatter.color(f'✅ Новый клиент готов к работе!',
                    'green'))
        await asyncio.sleep(1)


async def main():
    print_banner()
    config = load_config()
    proxy = load_proxy()
    api_id = config.getint('Telegram', 'api_id')
    api_hash = config.get('Telegram', 'api_hash')
    device_model = config.get('Telegram', 'device_model')
    system_version = config.get('Telegram', 'system_version')
    session_name = config.get('Telegram', 'session_name')
    command_prefix = config.get('Settings', 'command_prefix')
    print(TextFormatter.color('\n🚀 Запуск Herikku Userbot...', 'cyan'))
    client = TelegramClient(session_name, api_id, api_hash, device_model=
        device_model, system_version=system_version, proxy=proxy)
    from telethon.extensions import html
    client.parse_mode = html
    from core.formatting import markdown_to_html
    original_edit = client.edit_message

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
    client.edit_message = patched_edit
    print(TextFormatter.color('🔌 Подключение к Telegram...', 'cyan'))
    await client.start()
    me = await client.get_me()
    print(TextFormatter.color(
        f'✅ Авторизован как: {me.first_name} (@{me.username})', 'green'))
    print(TextFormatter.color(f'🔧 Префикс команд: {command_prefix}', 'cyan'))
    print(TextFormatter.color('\n🔍 Поиск дополнительных аккаунтов...', 'cyan'))
    await load_additional_accounts(api_id, api_hash, device_model,
        system_version, proxy, command_prefix)
    print(TextFormatter.color('\n📦 Настройка основного аккаунта...', 'cyan'))
    main_user_id = await setup_account(client, api_id, api_hash,
        device_model, system_version, proxy, command_prefix, is_main=True)
    if additional_clients:
        print(TextFormatter.color(
            f"""
📦 Загрузка модулей для {len(additional_clients)} дополнительных аккаунтов..."""
            , 'cyan'))
        for add_client in additional_clients:
            try:
                await setup_account(add_client, api_id, api_hash,
                    device_model, system_version, proxy, command_prefix,
                    is_main=False)
            except Exception as e:
                print(TextFormatter.color(
                    f'⚠️  Ошибка загрузки модулей: {e}', 'yellow'))
    await update_bot_commands(api_id, api_hash, device_model,
        system_version, proxy, command_prefix, main_user_id, client)
    total_modules = sum(len(modules) for modules in account_modules.values())
    print(TextFormatter.color(
        f'\n🚀 Herikku Userbot запущен! Загружено модулей: {total_modules}',
        'green'))
    print(TextFormatter.color(
        f'📱 Активных аккаунтов: {len(additional_clients) + 1}', 'green'))
    print(TextFormatter.color(
        f'📝 Используйте {command_prefix}help для списка команд', 'cyan'))
    if account_bots:
        print(TextFormatter.color(
            f'⚙️ Используйте {command_prefix}config для настроек\n', 'cyan'))
    asyncio.create_task(monitor_additional_clients(api_id, api_hash,
        device_model, system_version, proxy, command_prefix))
    tasks = [client.run_until_disconnected()]
    for user_id, bot in account_bots.items():
        tasks.append(bot.run_until_disconnected())
    for add_client in additional_clients:
        tasks.append(add_client.run_until_disconnected())
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].startswith('--web'):
        port = 5000
        if '=' in sys.argv[1]:
            try:
                port = int(sys.argv[1].split('=')[1])
            except ValueError:
                print('❌ Неверный формат порта. Используйте: --web=5000')
                sys.exit(1)
        from core.web_auth import start_web_auth
        print('=' * 50)
        print('🌐 РЕЖИМ ВЕБ-АВТОРИЗАЦИИ')
        print('=' * 50)
        start_web_auth(port)
    else:
        asyncio.run(main())
