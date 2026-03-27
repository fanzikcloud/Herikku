import os
import sys
import importlib.util
import subprocess
from telethon import events
from core.text_formatter import TextFormatter


def install_package(package_name):
    print(TextFormatter.color(f'📦 Установка зависимости: {package_name}',
        'yellow'))
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install',
            package_name, '-q'])
        print(TextFormatter.color(f'✅ {package_name} установлен', 'green'))
        return True
    except Exception as e:
        print(TextFormatter.color(f'❌ Ошибка установки {package_name}: {e}',
            'red'))
        return False


async def load_module(module_path, client, command_prefix, config, user_id,
    account_modules, loaded_modules, bot_start_time, add_client_callback=None):
    try:
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, type) and hasattr(item, 'NAME'
                ) and item.__name__ != 'Module':
                instance = item()
                if instance.DEPENDENCIES:
                    print(TextFormatter.color(
                        f'📦 Проверка зависимостей для {instance.NAME}...',
                        'yellow'))
                    for dep in instance.DEPENDENCIES:
                        try:
                            __import__(dep)
                            print(TextFormatter.color(
                                f'✅ {dep} уже установлен', 'green'))
                        except ImportError:
                            print(TextFormatter.color(
                                f'⚠️  {dep} не найден, устанавливаю...',
                                'yellow'))
                            if install_package(dep):
                                print(TextFormatter.color(
                                    f'✅ {dep} успешно установлен', 'green'))
                            else:
                                print(TextFormatter.color(
                                    f'❌ Не удалось установить {dep}', 'red'))
                                print(TextFormatter.color(
                                    f'⚠️  Модуль {instance.NAME} может работать некорректно'
                                    , 'yellow'))
                if user_id:
                    config_path = f'config_account_{user_id}.ini'
                    if user_id not in account_modules:
                        account_modules[user_id] = {}
                    modules_dict = account_modules[user_id]
                else:
                    config_path = 'config.ini'
                    modules_dict = loaded_modules
                await instance.init(client=client, command_prefix=
                    command_prefix, events=events, load_module=lambda path:
                    load_module(path, client, command_prefix, config,
                    user_id, account_modules, loaded_modules,
                    bot_start_time, add_client_callback), loaded_modules=
                    modules_dict, config=config, config_path=config_path,
                    install_package=install_package, bot_start_time=
                    bot_start_time)
                modules_dict[module_name] = instance
                if module_name == 'system' and hasattr(instance,
                    'add_client_callback') and add_client_callback:
                    instance.add_client_callback = add_client_callback
                print(TextFormatter.color(
                    f'✅ Модуль загружен: {instance.NAME}', 'green'))
                return instance
    except Exception as e:
        print(TextFormatter.color(
            f'❌ Ошибка загрузки модуля {module_path}: {e}', 'red'))
        import traceback
        traceback.print_exc()
        raise


async def load_builtin_modules(client, command_prefix, config, user_id,
    account_modules, loaded_modules, bot_start_time, add_client_callback=None):
    builtin_path = os.path.join('modules', 'builtin')
    if os.path.exists(builtin_path):
        for filename in os.listdir(builtin_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_path = os.path.join(builtin_path, filename)
                try:
                    await load_module(module_path, client, command_prefix,
                        config, user_id, account_modules, loaded_modules,
                        bot_start_time, add_client_callback)
                except Exception as e:
                    print(TextFormatter.color(
                        f'⚠️  Пропуск builtin модуля {filename}: {e}',
                        'yellow'))
    else:
        print(TextFormatter.color(
            '⚠️  Директория builtin модулей не найдена', 'yellow'))
    modules_path = 'modules'
    if os.path.exists(modules_path):
        for filename in os.listdir(modules_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_path = os.path.join(modules_path, filename)
                try:
                    await load_module(module_path, client, command_prefix,
                        config, user_id, account_modules, loaded_modules,
                        bot_start_time, add_client_callback)
                except Exception as e:
                    print(TextFormatter.color(
                        f'⚠️  Пропуск модуля {filename}: {e}', 'yellow'))
