from core.base_module import Module
import platform
import psutil
import socket
import time
from datetime import datetime


class FastfetchModule(Module):
    NAME = 'Fastfetch'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Красивый минималистичный вывод информации о системе'
    DEPENDENCIES = ['psutil']
    COMMANDS = {'fastfetch': 'Показать информацию о системе', 'ff':
        'Показать информацию о системе (короткая версия)'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.bot_start_time = bot_start_time

        def get_system_info():
            system = platform.system()
            release = platform.release()
            version = platform.version()
            machine = platform.machine()
            hostname = socket.gethostname()
            cpu_count = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Получение оперативной памяти
            memory = psutil.virtual_memory()
            memory_total = memory.total / 1024 ** 3
            memory_used = memory.used / 1024 ** 3
            memory_percent = memory.percent
            
            # Получение информации о диске
            try:
                disk = psutil.disk_usage('/')
                disk_total = disk.total / 1024 ** 3
                disk_used = disk.used / 1024 ** 3
                disk_percent = disk.percent
            except:
                disk_total, disk_used, disk_percent = 0, 0, 0
                
            # Расчет реального Uptime системы
            boot_time_timestamp = psutil.boot_time()
            uptime_seconds = time.time() - boot_time_timestamp
            days = int(uptime_seconds // (24 * 3600))
            hours = int((uptime_seconds % (24 * 3600)) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            uptime_str = f'{days}д {hours}ч {minutes}м'
            
            python_version = platform.python_version()
            return {'system': system, 'release': release, 'version':
                version, 'machine': machine, 'hostname': hostname, 
                'cpu_count': cpu_count, 'cpu_percent': cpu_percent, 
                'memory_total': memory_total, 'memory_used': memory_used, 
                'memory_percent': memory_percent, 'disk_total': disk_total, 
                'disk_used': disk_used, 'disk_percent': disk_percent, 'uptime':
                uptime_str, 'python_version': python_version}

        def create_fastfetch_output(info, username):
            # Минималистичные односимвольные эмодзи-значки вместо громоздких ASCII логотипов
            # Это полностью исключает проблему съезжания шрифтов в мобильных клиентах Telegram!
            if info['system'] == 'Windows':
                sys_icon = '🪟'
            elif info['system'] == 'Linux':
                sys_icon = '🐧'
            elif info['system'] == 'Darwin':
                sys_icon = '🍎'
            else:
                sys_icon = '💻'
                
            os_name = f"{info['system']} {info['release']}"
            kernel = info['version'].split(' ')[0] if ' ' in info['version'] else info['version']
            kernel = kernel.replace('#', '')[:18]
            
            # Минималистичное форматирование с фиксированными отступами
            output = f"<b>{sys_icon} {username}@{info['hostname']}</b>\n"
            output += f"<code>├─ OS:     {os_name}</code>\n"
            output += f"<code>├─ Kernel: {kernel} ({info['machine']})</code>\n"
            output += f"<code>├─ CPU:    {info['cpu_percent']}% ({info['cpu_count']} Cores)</code>\n"
            output += f"<code>├─ RAM:    {info['memory_used']:.1f}/{info['memory_total']:.1f} GB ({info['memory_percent']}%)</code>\n"
            output += f"<code>├─ Disk:   {info['disk_used']:.1f}/{info['disk_total']:.1f} GB ({info['disk_percent']}%)</code>\n"
            output += f"<code>├─ Uptime: {info['uptime']}</code>\n"
            output += f"<code>└─ Python: {info['python_version']}</code>"
            return output

        async def fastfetch_handler(event):
            if not event.text:
                return
            if not (event.text.startswith(f'{self.prefix}fastfetch') or
                event.text.startswith(f'{self.prefix}ff')):
                return
            me = await self.client.get_me()
            username = me.first_name or me.username or 'User'
            info = get_system_info()
            output = create_fastfetch_output(info, username)
            await event.edit(output)
            
        client.add_event_handler(fastfetch_handler, events.NewMessage(
            outgoing=True))
