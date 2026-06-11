from core.base_module import Module
import os
import importlib.util
import aiohttp
import tempfile
import re


class ModuleManagerModule(Module):
    NAME = 'Module Manager'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Загрузка и управление модулями'
    DEPENDENCIES = []
    COMMANDS = {'lm': 'Загрузить модуль (ответьте на .py файл)', 'dlm':
        'Скачать и загрузить модуль по ссылке (например: .dlm https://example.com/module.py)'
        }

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.load_module = load_module

        async def load_module_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}lm'):
                return
            if not event.is_reply:
                await event.edit(
                    f'❌ Ответьте этой командой на сообщение с .py файлом')
                return
            replied_msg = await event.get_reply_message()
            if not replied_msg.media or not replied_msg.document:
                await event.edit('❌ Сообщение не содержит файл')
                return
            filename = replied_msg.file.name
            if not filename or not filename.endswith('.py'):
                await event.edit('❌ Файл должен иметь расширение .py')
                return
            await event.edit('📥 Скачиваю модуль...')
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_file = os.path.join(temp_dir, filename)
                    await replied_msg.download_media(temp_file)
                    if not await self.validate_module(temp_file):
                        await event.edit(
                            """❌ Это не валидный модуль Herikku
💡 Модуль должен содержать функцию `setup()` и наследоваться от BaseModule/Module"""
                            )
                        return
                    module_path = os.path.join('modules', filename)
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(module_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    await event.edit('🔄 Загружаю модуль...')
                    await self.load_module(module_path)
                    await event.edit(f'✅ Модуль `{filename}` успешно загружен!'
                        )
            except Exception as e:
                import traceback
                traceback.print_exc()
                await event.edit(f'❌ Ошибка загрузки модуля:\n```{str(e)}```')

        async def download_module_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}dlm'
                ):
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.edit(
                    f"""❌ Использование: `{self.prefix}dlm <url>`

💡 Пример:
`{self.prefix}dlm https://example.com/module.py`"""
                    )
                return
            url = parts[1].strip()
            if not url.startswith(('http://', 'https://')):
                await event.edit(
                    '❌ Неверный URL. Должен начинаться с http:// или https://')
                return
            filename = url.split('/')[-1]
            if not filename.endswith('.py'):
                if '?' in filename:
                    filename = filename.split('?')[0]
                if not filename.endswith('.py'):
                    filename += '.py'
            await event.edit(f'📥 Скачиваю модуль с {url}...')
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            await event.edit(
                                f'❌ Ошибка скачивания: HTTP {response.status}')
                            return
                        content = await response.text()
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_file = os.path.join(temp_dir, filename)
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    if not await self.validate_module(temp_file):
                        await event.edit(
                            """❌ Это не валидный модуль Herikku
💡 Модуль должен содержать функцию `setup()` и наследоваться от BaseModule/Module"""
                            )
                        return
                    module_path = os.path.join('modules', filename)
                    with open(module_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    await event.edit('🔄 Загружаю модуль...')
                    await self.load_module(module_path)
                    await event.edit(
                        f'✅ Модуль `{filename}` успешно скачан и загружен!')
            except aiohttp.ClientError as e:
                await event.edit(f'❌ Ошибка сети: {str(e)}')
            except Exception as e:
                import traceback
                traceback.print_exc()
                await event.edit(f'❌ Ошибка: ```{str(e)}```')
        client.add_event_handler(load_module_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(download_module_handler, events.NewMessage
            (outgoing=True))

    async def validate_module(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'from core.base_module import Module' not in content:
                print('❌ Валидация: нет импорта Module')
                return False
            if 'class ' not in content or '(Module)' not in content:
                print('❌ Валидация: нет класса наследующего Module')
                return False
            if 'async def init(' not in content:
                print('❌ Валидация: нет метода init()')
                return False
            try:
                compile(content, file_path, 'exec')
            except SyntaxError as e:
                print(f'❌ Валидация: синтаксическая ошибка - {e}')
                return False
            print('✅ Валидация: модуль прошел проверку')
            return True
        except Exception as e:
            print(f'❌ Ошибка валидации модуля: {e}')
            import traceback
            traceback.print_exc()
            return False
