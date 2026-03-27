from core.base_module import Module
import platform
import psutil
import socket
from datetime import datetime


class FastfetchModule(Module):
    NAME = 'Fastfetch'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Красивый вывод информации о системе'
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
            processor = platform.processor()
            hostname = socket.gethostname()
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_total = memory.total / 1024 ** 3
            memory_used = memory.used / 1024 ** 3
            memory_percent = memory.percent
            disk = psutil.disk_usage('/')
            disk_total = disk.total / 1024 ** 3
            disk_used = disk.used / 1024 ** 3
            disk_percent = disk.percent
            uptime = datetime.now() - self.bot_start_time
            uptime_str = (
                f'{uptime.days}д {uptime.seconds // 3600}ч {uptime.seconds // 60 % 60}м'
                )
            python_version = platform.python_version()
            return {'system': system, 'release': release, 'version':
                version, 'machine': machine, 'processor': processor,
                'hostname': hostname, 'cpu_count': cpu_count,
                'cpu_count_logical': cpu_count_logical, 'cpu_freq':
                cpu_freq, 'cpu_percent': cpu_percent, 'memory_total':
                memory_total, 'memory_used': memory_used, 'memory_percent':
                memory_percent, 'disk_total': disk_total, 'disk_used':
                disk_used, 'disk_percent': disk_percent, 'uptime':
                uptime_str, 'python_version': python_version}

        def create_fastfetch_output(info, username):
            if info['system'] == 'Windows':
                logo = ['████████  ████████', '████████  ████████',
                    '████████  ████████', '████████  ████████', '',
                    '████████  ████████', '████████  ████████',
                    '████████  ████████', '████████  ████████']
                color = '🟦'
            elif info['system'] == 'Linux':
                logo = ['        🐧        ', '       🐧🐧       ',
                    '      🐧  🐧      ', '     🐧    🐧     ', '    🐧🐧🐧🐧🐧    ',
                    '   🐧        🐧   ', '  🐧          🐧  ',
                    ' 🐧            🐧 ', '🐧              🐧']
                color = '🟨'
            elif info['system'] == 'Darwin':
                logo = ['       🍎🍎🍎      ', '     🍎🍎🍎🍎🍎    ',
                    '    🍎🍎    🍎🍎   ', '   🍎🍎      🍎🍎  ', '  🍎🍎        🍎🍎 ',
                    '  🍎🍎        🍎🍎 ', '   🍎🍎      🍎🍎  ', '    🍎🍎🍎🍎🍎🍎   ',
                    '      🍎🍎🍎🍎     ']
                color = '⬜'
            else:
                logo = ['  ╔══════════╗  ', '  ║          ║  ',
                    '  ║  SYSTEM  ║  ', '  ║          ║  ', '  ╚══════════╝  ']
                color = '⬜'
            output = f'```\n'
            output += f"{username}@{info['hostname']}\n"
            output += f"{'─' * (len(username) + len(info['hostname']) + 1)}\n"
            lines = [f"{color} OS        {info['system']} {info['release']}",
                f"{color} Host      {info['hostname']}",
                f"{color} Kernel    {info['version'][:50]}",
                f"{color} Arch      {info['machine']}",
                f"{color} CPU       {info['processor'][:40] if info['processor'] else 'Unknown'}"
                ,
                f"{color} CPU Cores {info['cpu_count']} ({info['cpu_count_logical']} threads)"
                , f"{color} CPU Usage {info['cpu_percent']}%",
                f"{color} Memory    {info['memory_used']:.1f}GB / {info['memory_total']:.1f}GB ({info['memory_percent']}%)"
                ,
                f"{color} Disk      {info['disk_used']:.1f}GB / {info['disk_total']:.1f}GB ({info['disk_percent']}%)"
                , f"{color} Uptime    {info['uptime']}",
                f"{color} Python    {info['python_version']}"]
            max_lines = max(len(logo), len(lines))
            for i in range(max_lines):
                logo_line = logo[i] if i < len(logo) else ' ' * 18
                info_line = lines[i] if i < len(lines) else ''
                output += f'{logo_line}  {info_line}\n'
            output += '```'
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
