import random
import string
import asyncio
from telethon import functions, types


async def setup_bot_commands(client, bot_username):
    try:
        botfather = await client.get_entity('@BotFather')
        print('🔧 Настройка команд бота...')
        await client.send_message(botfather, '/setcommands')
        await asyncio.sleep(1.5)
        await client.send_message(botfather, f'@{bot_username}')
        await asyncio.sleep(1.5)
        await client.send_message(botfather, 'help - Показать список модулей')
        await asyncio.sleep(1)
        print('✅ Команды бота настроены')
        return True
    except Exception as e:
        print(f'⚠️ Не удалось настроить команды: {e}')
        return False


async def create_bot_via_botfather(client):
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
    bot_username = f'herikku_{random_suffix}_bot'
    bot_name = f'Herikku {random_suffix}'
    print(f'🤖 Создание бота: @{bot_username}')
    try:
        botfather = await client.get_entity('@BotFather')
        await client.send_message(botfather, '/newbot')
        await asyncio.sleep(1.5)
        await client.send_message(botfather, bot_name)
        await asyncio.sleep(1.5)
        await client.send_message(botfather, bot_username)
        await asyncio.sleep(2.5)
        messages = await client.get_messages(botfather, limit=5)
        token = None
        for msg in messages:
            if not msg.text:
                continue
            if 'Done!' in msg.text or 'token' in msg.text.lower():
                import re
                token_pattern = '(\\d{8,10}:[A-Za-z0-9_-]{35})'
                match = re.search(token_pattern, msg.text)
                if match:
                    token = match.group(1)
                    break
                lines = msg.text.split('\n')
                for line in lines:
                    line = line.strip()
                    line = line.replace('`', '').replace('*', '').replace('_',
                        '')
                    if ':' in line and len(line) > 40:
                        parts = line.split(':')
                        if len(parts) == 2 and parts[0].isdigit() and len(parts
                            [0]) >= 8:
                            token = line
                            break
                if token:
                    break
        if token:
            print(f'✅ Бот создан: @{bot_username}')
            print(f'🔑 Токен получен')
            print('🔧 Настройка inline режима...')
            await client.send_message(botfather, '/setinline')
            await asyncio.sleep(1.5)
            await client.send_message(botfather, f'@{bot_username}')
            await asyncio.sleep(1.5)
            await client.send_message(botfather, '⚙️ Настройки Herikku')
            await asyncio.sleep(1)
            print('✅ Inline режим включен')
            await setup_bot_commands(client, bot_username)
            return {'token': token, 'username': bot_username, 'name': bot_name}
        print('⚠️ Не удалось автоматически получить токен')
        print('📝 Создайте бота вручную через @BotFather:')
        print('   1. Отправьте /newbot')
        print(f'   2. Введите имя: {bot_name}')
        print(f'   3. Введите username: {bot_username}')
        print('   4. Скопируйте токен и вставьте ниже')
        return None
    except Exception as e:
        print(f'❌ Ошибка создания бота: {e}')
        return None


async def update_bot_commands_from_modules(client, bot_username,
    loaded_modules, command_prefix):
    try:
        botfather = await client.get_entity('@BotFather')
        print('🔧 Обновление команд бота...')
        commands = []
        commands.append('help - Показать список модулей')
        commands.append('config - Открыть настройки')
        for module_name, module_instance in loaded_modules.items():
            if hasattr(module_instance, 'COMMANDS'
                ) and module_instance.COMMANDS:
                for cmd, desc in list(module_instance.COMMANDS.items())[:1]:
                    commands.append(f'{cmd} - {desc}')
        commands = commands[:10]
        await client.send_message(botfather, '/setcommands')
        await asyncio.sleep(1.5)
        await client.send_message(botfather, f'@{bot_username}')
        await asyncio.sleep(1.5)
        commands_text = '\n'.join(commands)
        await client.send_message(botfather, commands_text)
        await asyncio.sleep(1)
        print(f'✅ Обновлено команд бота: {len(commands)}')
        return True
    except Exception as e:
        print(f'⚠️ Не удалось обновить команды: {e}')
        return False
