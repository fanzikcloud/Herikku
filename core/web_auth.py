import asyncio
import time
from flask import Flask, request, jsonify, Response
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import threading
import configparser
import os


class WebAuthServer:

    def __init__(self, api_id, api_hash, device_model, system_version,
        session_name, proxy_config=None, port=5000):
        self.api_id = api_id
        self.api_hash = api_hash
        self.device_model = device_model
        self.system_version = system_version
        self.session_name = session_name
        self.proxy_config = proxy_config
        self.port = port
        self.app = Flask(__name__)
        self.auth_sessions = {}
        self.authorized_accounts = []
        self.first_account = True
        self.setup_routes()

    def run_in_new_loop(self, coro):

        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(coro)
                return result
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise
            finally:
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    loop.run_until_complete(asyncio.gather(*pending,
                        return_exceptions=True))
                except:
                    pass
                loop.close()
        import threading
        result_container = {}
        exception_container = {}

        def thread_target():
            try:
                result_container['result'] = run()
            except Exception as e:
                exception_container['exception'] = e
        thread = threading.Thread(target=thread_target)
        thread.start()
        thread.join(timeout=30)
        if 'exception' in exception_container:
            raise exception_container['exception']
        return result_container.get('result')

    def run_in_session_loop(self, session_id, coro):
        if session_id not in self.auth_sessions:
            raise ValueError(f'Session {session_id} not found')
        session = self.auth_sessions[session_id]
        loop = session['loop']
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result(timeout=30)

    def setup_routes(self):

        def index():
            html_path = os.path.join(os.path.dirname(__file__), 'assets',
                'auth.html')
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                return 'Error: auth.html not found', 404

        def static_files(filename):
            static_path = os.path.join(os.path.dirname(__file__), 'assets',
                filename)
            print(f'📁 Запрос статического файла: {filename}')
            print(f'📂 Полный путь: {static_path}')
            print(f'✓ Файл существует: {os.path.exists(static_path)}')
            try:
                with open(static_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if filename.endswith('.css'):
                    return Response(content, mimetype='text/css')
                elif filename.endswith('.js'):
                    return Response(content, mimetype='application/javascript')
                else:
                    return content
            except FileNotFoundError as e:
                print(f'❌ Файл не найден: {e}')
                return f'Error: {filename} not found', 404
            except Exception as e:
                print(f'❌ Ошибка: {e}')
                return f'Error: {str(e)}', 500
        self.app.add_url_rule('/', 'index', index)
        self.app.add_url_rule('/assets/<path:filename>', 'assets', static_files
            )

        def send_code():
            data = request.json
            phone = data.get('phone', '').strip()
            if not phone:
                return jsonify({'success': False, 'error':
                    'Номер телефона не указан'})
            try:
                if self.first_account:
                    session_id = self.session_name
                    if os.path.exists(f'{self.session_name}.session'):
                        self.first_account = False
                else:
                    session_id = f'herikku_account_{int(time.time())}'
                loop_ready = threading.Event()
                session_loop = None
                session_thread = None

                def run_session_loop():
                    nonlocal session_loop
                    session_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(session_loop)
                    loop_ready.set()
                    session_loop.run_forever()
                session_thread = threading.Thread(target=run_session_loop,
                    daemon=True)
                session_thread.start()
                loop_ready.wait()

                async def connect_and_send():
                    client = TelegramClient(session_id, self.api_id, self.
                        api_hash, device_model=self.device_model,
                        system_version=self.system_version, proxy=self.
                        proxy_config)
                    await client.connect()
                    if await client.is_user_authorized():
                        me = await client.get_me()
                        await client.disconnect()
                        return {'success': True, 'already_authorized': True,
                            'user': {'first_name': me.first_name,
                            'username': me.username, 'id': me.id},
                            'session_id': session_id, 'client': None,
                            'should_stop_loop': True}
                    await client.send_code_request(phone)
                    return {'success': True, 'session_id': session_id,
                        'already_authorized': False, 'client': client,
                        'should_stop_loop': False}
                future = asyncio.run_coroutine_threadsafe(connect_and_send(
                    ), session_loop)
                result = future.result(timeout=30)
                if result.get('already_authorized'):
                    self.authorized_accounts.append(session_id)
                    if session_id == self.session_name:
                        self.first_account = False
                    if result.get('should_stop_loop'):
                        session_loop.call_soon_threadsafe(session_loop.stop)
                    return jsonify(result)
                self.auth_sessions[session_id] = {'client': result['client'
                    ], 'phone': phone, 'step': 'code', 'loop': session_loop,
                    'thread': session_thread}
                return jsonify({'success': True, 'session_id': session_id,
                    'already_authorized': False})
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': str(e)})
        self.app.add_url_rule('/api/send_code', 'send_code', send_code,
            methods=['POST'])

        def verify_code():
            data = request.json
            session_id = data.get('session_id')
            code = data.get('code', '').strip()
            if not session_id or session_id not in self.auth_sessions:
                return jsonify({'success': False, 'error': 'Сессия не найдена'}
                    )
            if not code:
                return jsonify({'success': False, 'error': 'Код не указан'})
            session = self.auth_sessions[session_id]
            client = session['client']
            phone = session['phone']
            try:

                async def sign_in():
                    try:
                        await client.sign_in(phone, code)
                        me = await client.get_me()
                        return {'success': True, 'needs_password': False,
                            'user': {'first_name': me.first_name,
                            'username': me.username, 'id': me.id}}
                    except SessionPasswordNeededError:
                        return {'success': True, 'needs_password': True}
                    except PhoneCodeInvalidError:
                        return {'success': False, 'error': 'Неверный код'}
                result = self.run_in_session_loop(session_id, sign_in())
                if result.get('needs_password'):
                    session['step'] = 'password'
                elif result.get('success'):
                    self.authorized_accounts.append(session_id)
                    if session_id == self.session_name:
                        self.first_account = False
                    try:

                        async def disconnect():
                            if client.is_connected():
                                await client.disconnect()
                        disconnect_future = asyncio.run_coroutine_threadsafe(
                            disconnect(), session['loop'])
                        disconnect_future.result(timeout=5)
                        session['loop'].call_soon_threadsafe(session['loop'
                            ].stop)
                    except Exception as e:
                        print(f'⚠️  Ошибка отключения клиента: {e}')
                    del self.auth_sessions[session_id]
                return jsonify(result)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': str(e)})
        self.app.add_url_rule('/api/verify_code', 'verify_code',
            verify_code, methods=['POST'])

        def verify_password():
            data = request.json
            session_id = data.get('session_id')
            password = data.get('password', '')
            if not session_id or session_id not in self.auth_sessions:
                return jsonify({'success': False, 'error': 'Сессия не найдена'}
                    )
            if not password:
                return jsonify({'success': False, 'error': 'Пароль не указан'})
            session = self.auth_sessions[session_id]
            client = session['client']
            try:

                async def sign_in_password():
                    try:
                        await client.sign_in(password=password)
                        me = await client.get_me()
                        return {'success': True, 'user': {'first_name': me.
                            first_name, 'username': me.username, 'id': me.id}}
                    except Exception as e:
                        return {'success': False, 'error':
                            f'Неверный пароль: {str(e)}'}
                result = self.run_in_session_loop(session_id,
                    sign_in_password())
                if result.get('success'):
                    self.authorized_accounts.append(session_id)
                    if session_id == self.session_name:
                        self.first_account = False
                    try:

                        async def disconnect():
                            if client.is_connected():
                                await client.disconnect()
                        disconnect_future = asyncio.run_coroutine_threadsafe(
                            disconnect(), session['loop'])
                        disconnect_future.result(timeout=5)
                        session['loop'].call_soon_threadsafe(session['loop'
                            ].stop)
                    except Exception as e:
                        print(f'⚠️  Ошибка отключения клиента: {e}')
                    del self.auth_sessions[session_id]
                return jsonify(result)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': str(e)})
        self.app.add_url_rule('/api/verify_password', 'verify_password',
            verify_password, methods=['POST'])

    def run(self):
        print(f'\n🌐 Веб-интерфейс запущен: http://localhost:{self.port}')
        print(f'📱 Откройте браузер для авторизации аккаунтов')
        print(f'💡 После авторизации нажмите Ctrl+C для запуска юзербота\n')
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False,
                threaded=True)
        except KeyboardInterrupt:
            print('\n\n🛑 Веб-сервер остановлен')
            if self.authorized_accounts:
                print(
                    f'\n✅ Авторизовано аккаунтов: {len(self.authorized_accounts)}'
                    )
                print('🚀 Запускаю юзербот...\n')
                import subprocess
                import sys
                subprocess.Popen([sys.executable, 'main.py'])
            else:
                print('\n⚠️  Нет авторизованных аккаунтов')
                print('💡 Запустите снова для авторизации')


def start_web_auth(port=5000):
    config = configparser.ConfigParser()
    config_created = False
    if not os.path.exists('config.ini'):
        print('📝 Файл config.ini не найден, создаю из примера...')
        if os.path.exists('config.ini.example'):
            import shutil
            shutil.copy('config.ini.example', 'config.ini')
            print('✅ config.ini создан из config.ini.example')
            config_created = True
        else:
            print('⚠️  config.ini.example не найден')
            config_created = True
    config.read('config.ini', encoding='utf-8')
    needs_setup = False
    if not config.has_section('Telegram'):
        needs_setup = True
    else:
        try:
            api_id = config.get('Telegram', 'api_id', fallback='YOUR_API_ID')
            api_hash = config.get('Telegram', 'api_hash', fallback=
                'YOUR_API_HASH')
            if api_id in ['YOUR_API_ID', ''] or api_hash in ['YOUR_API_HASH',
                '']:
                needs_setup = True
            else:
                try:
                    int(api_id)
                except ValueError:
                    needs_setup = True
        except (configparser.NoOptionError, ValueError):
            needs_setup = True
    if needs_setup:
        print('\n' + '=' * 50)
        print('📋 НАСТРОЙКА API CREDENTIALS')
        print('=' * 50)
        print('Получите API ID и API Hash на https://my.telegram.org')
        print('=' * 50 + '\n')
        api_id = input('Введите API ID: ').strip()
        api_hash = input('Введите API Hash: ').strip()
        device_model = input('Модель устройства (Enter = Herikku): ').strip(
            ) or 'Herikku'
        system_version = input('Версия системы (Enter = 1.0): ').strip(
            ) or '1.0'
        session_name = input('Имя сессии (Enter = herikku_session): ').strip(
            ) or 'herikku_session'
        command_prefix = input('Префикс команд (Enter = .): ').strip() or '.'
        if not config.has_section('Telegram'):
            config.add_section('Telegram')
        config.set('Telegram', 'api_id', api_id)
        config.set('Telegram', 'api_hash', api_hash)
        config.set('Telegram', 'device_model', device_model)
        config.set('Telegram', 'system_version', system_version)
        config.set('Telegram', 'session_name', session_name)
        if not config.has_section('Settings'):
            config.add_section('Settings')
        config.set('Settings', 'command_prefix', command_prefix)
        if not config.has_section('InlineBot'):
            config.add_section('InlineBot')
        config.set('InlineBot', 'token', '')
        config.set('InlineBot', 'username', '')
        config.set('InlineBot', 'name', '')
        with open('config.ini', 'w', encoding='utf-8') as f:
            config.write(f)
        print('\n✅ config.ini сохранен!')
    if not os.path.exists('proxy.ini'):
        print('📝 Файл proxy.ini не найден, создаю из примера...')
        if os.path.exists('proxy.ini.example'):
            import shutil
            shutil.copy('proxy.ini.example', 'proxy.ini')
            print('✅ proxy.ini создан из proxy.ini.example')
        else:
            proxy_config = configparser.ConfigParser()
            proxy_config['Proxy'] = {'enabled': 'no', 'type': 'socks5',
                'host': '127.0.0.1', 'port': '1080', 'username': '',
                'password': ''}
            with open('proxy.ini', 'w', encoding='utf-8') as f:
                proxy_config.write(f)
            print('✅ proxy.ini создан с настройками по умолчанию')
    try:
        api_id = config.getint('Telegram', 'api_id')
        api_hash = config.get('Telegram', 'api_hash')
        device_model = config.get('Telegram', 'device_model', fallback=
            'Herikku')
        system_version = config.get('Telegram', 'system_version', fallback=
            '1.0')
        session_name = config.get('Telegram', 'session_name', fallback=
            'herikku_session')
    except (configparser.NoOptionError, ValueError) as e:
        print(f'\n❌ Ошибка чтения конфигурации: {e}')
        print('📝 Проверьте config.ini')
        return
    proxy_config = None
    if os.path.exists('proxy.ini'):
        proxy = configparser.ConfigParser()
        proxy.read('proxy.ini', encoding='utf-8')
        if proxy.has_section('Proxy'):
            enabled = proxy.get('Proxy', 'enabled', fallback='no').lower(
                ) == 'yes'
            if enabled:
                import socks
                proxy_type = proxy.get('Proxy', 'type', fallback='socks5'
                    ).lower()
                proxy_host = proxy.get('Proxy', 'host', fallback='127.0.0.1')
                proxy_port = proxy.getint('Proxy', 'port', fallback=1080)
                proxy_username = proxy.get('Proxy', 'username', fallback=''
                    ) or None
                proxy_password = proxy.get('Proxy', 'password', fallback=''
                    ) or None
                if proxy_type == 'socks5':
                    ptype = socks.SOCKS5
                elif proxy_type == 'socks4':
                    ptype = socks.SOCKS4
                elif proxy_type == 'http':
                    ptype = socks.HTTP
                else:
                    ptype = socks.SOCKS5
                proxy_config = (ptype, proxy_host, proxy_port, True,
                    proxy_username, proxy_password)
                print(
                    f'🔒 Прокси включен: {proxy_type}://{proxy_host}:{proxy_port}'
                    )
    print('\n' + '=' * 50)
    print('✅ Конфигурация загружена')
    print('=' * 50)
    server = WebAuthServer(api_id, api_hash, device_model, system_version,
        session_name, proxy_config, port)
    server.run()
