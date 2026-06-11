import os
import configparser
import socks
from telethon import connection
from core.text_formatter import TextFormatter

PROXY_FILE = 'proxy.ini'


def load_proxy():
    if not os.path.exists(PROXY_FILE):
        print(TextFormatter.color(
            '⚠️  Файл proxy.ini не найден, прокси не используется', 'yellow'))
        return None
    proxy_config = configparser.ConfigParser()
    proxy_config.read(PROXY_FILE, encoding='utf-8')
    if not proxy_config.has_section('Proxy'):
        return None
    enabled = proxy_config.get('Proxy', 'enabled', fallback='no').lower()
    if enabled not in ['yes', 'true', '1']:
        print(TextFormatter.color('ℹ️  Прокси отключен в конфигурации', 'cyan')
            )
        return None
    proxy_type = proxy_config.get('Proxy', 'type', fallback='socks5').lower()
    host = proxy_config.get('Proxy', 'host', fallback='127.0.0.1')
    port = proxy_config.getint('Proxy', 'port', fallback=1080)
    username = proxy_config.get('Proxy', 'username', fallback='').strip()
    password = proxy_config.get('Proxy', 'password', fallback='').strip()
    
    # Поддержка MTProto прокси
    if proxy_type in ['mtproto', 'mtproxy']:
        # Для MTProto прокси secret передается в password или username
        secret = password if password else username
        if not secret:
            secret = '00000000000000000000000000000000' # Дефолтный секрет если не указан
        
        # Для MTProto Telethon использует специальный кортеж: (host, port, secret)
        proxy = (host, port, secret)
        print(TextFormatter.color(
            f'🔒 Прокси: MTPROTO {host}:{port}', 'green'))
        return proxy

    if proxy_type == 'socks5':
        ptype = socks.SOCKS5
    elif proxy_type == 'socks4':
        ptype = socks.SOCKS4
    elif proxy_type == 'http':
        ptype = socks.HTTP
    else:
        print(TextFormatter.color(f'❌ Неизвестный тип прокси: {proxy_type}',
            'red'))
        return None
        
    proxy = ptype, host, port
    if username and password:
        proxy = ptype, host, port, True, username, password
        print(TextFormatter.color(
            f'🔒 Прокси: {proxy_type.upper()} {host}:{port} (с авторизацией)',
            'green'))
    else:
        print(TextFormatter.color(
            f'🔒 Прокси: {proxy_type.upper()} {host}:{port}', 'green'))
    return proxy


def is_mtproto_proxy(proxy):
    """Проверяет, является ли прокси прокси-сервером MTProto"""
    if proxy and isinstance(proxy, tuple) and len(proxy) == 3 and isinstance(proxy[2], str):
        # Если третий элемент - строка, это secret для MTProto
        return True
    return False
