import os
import configparser
from core.text_formatter import TextFormatter
CONFIG_FILE = 'config.ini'
PROXY_FILE = 'proxy.ini'


def load_config():
    config = configparser.ConfigParser()
    needs_setup = False
    if not os.path.exists(CONFIG_FILE):
        needs_setup = True
    else:
        config.read(CONFIG_FILE, encoding='utf-8')
        if config.has_section('Telegram'):
            api_id_str = config.get('Telegram', 'api_id', fallback=
                'YOUR_API_ID')
            api_hash_str = config.get('Telegram', 'api_hash', fallback=
                'YOUR_API_HASH')
            if api_id_str in ('YOUR_API_ID', '') or api_hash_str in (
                'YOUR_API_HASH', ''):
                needs_setup = True
        else:
            needs_setup = True
    if needs_setup:
        print(TextFormatter.color(
            '⚙️  Первый запуск - настройка конфигурации', 'cyan'))
        print(TextFormatter.color(
            '📱 Получите API ID и API Hash на https://my.telegram.org/apps',
            'yellow'))
        api_id = input('Введите API ID: ').strip()
        api_hash = input('Введите API Hash: ').strip()
        device_model = input(
            'Введите модель устройства (по умолчанию: Herikku): ').strip(
            ) or 'Herikku'
        system_version = input('Введите версию системы (по умолчанию: 1.0): '
            ).strip() or '1.0'
        session_name = input(
            'Введите имя сессии (по умолчанию: herikku_session): ').strip(
            ) or 'herikku_session'
        command_prefix = input('Введите префикс команд (по умолчанию: .): '
            ).strip() or '.'
        config['Telegram'] = {'api_id': api_id, 'api_hash': api_hash,
            'device_model': device_model, 'system_version': system_version,
            'session_name': session_name}
        config['Settings'] = {'command_prefix': command_prefix}
        config['InlineBot'] = {'token': '', 'username': '', 'name': ''}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        print(TextFormatter.color('✅ Конфигурация сохранена!', 'green'))
    elif not config.has_section('InlineBot'):
        config.add_section('InlineBot')
        config.set('InlineBot', 'token', '')
        config.set('InlineBot', 'username', '')
        config.set('InlineBot', 'name', '')
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
    return config


def get_account_config(user_id, account_configs, base_config_file=CONFIG_FILE):
    if user_id in account_configs:
        return account_configs[user_id]
    config_file = f'config_account_{user_id}.ini'
    config = configparser.ConfigParser()
    base_config = configparser.ConfigParser()
    base_config.read(base_config_file, encoding='utf-8')
    if os.path.exists(config_file):
        config.read(config_file, encoding='utf-8')
        needs_save = False
        if not config.has_section('Telegram') and base_config.has_section(
            'Telegram'):
            config.add_section('Telegram')
            for key, value in base_config.items('Telegram'):
                config.set('Telegram', key, value)
            needs_save = True
        if not config.has_section('InlineBot'):
            config.add_section('InlineBot')
            config.set('InlineBot', 'token', '')
            config.set('InlineBot', 'username', '')
            config.set('InlineBot', 'name', '')
            needs_save = True
        if needs_save:
            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)
    else:
        if base_config.has_section('Telegram'):
            config.add_section('Telegram')
            for key, value in base_config.items('Telegram'):
                config.set('Telegram', key, value)
        if base_config.has_section('Settings'):
            config.add_section('Settings')
            for key, value in base_config.items('Settings'):
                config.set('Settings', key, value)
        config.add_section('InlineBot')
        config.set('InlineBot', 'token', '')
        config.set('InlineBot', 'username', '')
        config.set('InlineBot', 'name', '')
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        print(TextFormatter.color(
            f'✅ Создан конфиг для аккаунта {user_id}: {config_file}', 'green'))
    account_configs[user_id] = config
    return config


def save_account_config(user_id, account_configs):
    if user_id in account_configs:
        config_file = f'config_account_{user_id}.ini'
        with open(config_file, 'w', encoding='utf-8') as f:
            account_configs[user_id].write(f)
