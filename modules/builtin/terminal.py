from core.base_module import Module
import subprocess
import asyncio


class TerminalModule(Module):
    NAME = 'Terminal'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Выполнение команд в терминале'
    DEPENDENCIES = []
    COMMANDS = {'terminal':
        'Выполнить команду в терминале (.terminal <команда>)', 't':
        'Выполнить команду в терминале (.t <команда>)'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def terminal_handler(event):
            if not event.text:
                return
            if not (event.text.startswith(f'{self.prefix}terminal') or
                event.text.startswith(f'{self.prefix}t ')):
                if event.text == f'{self.prefix}t':
                    await event.edit(
                        f"""**💻 Terminal**

Использование:
`{self.prefix}t <команда>`
`{self.prefix}terminal <команда>`

Пример:
`{self.prefix}t dir`
`{self.prefix}terminal echo Hello`"""
                        )
                    return
                return
            if event.text.startswith(f'{self.prefix}terminal'):
                parts = event.text.split(maxsplit=1)
                if len(parts) < 2:
                    await event.edit(
                        f"""**💻 Terminal**

Использование:
`{self.prefix}terminal <команда>`

Пример:
`{self.prefix}terminal dir`"""
                        )
                    return
                command = parts[1]
            else:
                parts = event.text.split(maxsplit=1)
                if len(parts) < 2:
                    await event.edit(
                        f"""**💻 Terminal**

Использование:
`{self.prefix}t <команда>`

Пример:
`{self.prefix}t dir`"""
                        )
                    return
                command = parts[1]
            await event.edit(f'**💻 Выполнение команды...**\n\n`$ {command}`')
            try:
                process = await asyncio.create_subprocess_shell(command,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.
                    subprocess.PIPE, shell=True)
                stdout, stderr = await process.communicate()
                output = ''
                if stdout:
                    try:
                        output += stdout.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            output += stdout.decode('cp1251')
                        except:
                            output += stdout.decode('utf-8', errors='ignore')
                if stderr:
                    try:
                        error_text = stderr.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            error_text = stderr.decode('cp1251')
                        except:
                            error_text = stderr.decode('utf-8', errors='ignore'
                                )
                    if error_text:
                        output += f'\n\n❌ Ошибки:\n{error_text}'
                if not output.strip():
                    output = '✅ Команда выполнена успешно (без вывода)'
                if len(output) > 4000:
                    output = output[:4000] + '\n\n... (вывод обрезан)'
                result = f'**💻 Terminal**\n\n`$ {command}`\n\n'
                result += f'**Код возврата:** `{process.returncode}`\n\n'
                result += f'**Вывод:**\n```\n{output}\n```'
                await event.edit(result)
            except Exception as e:
                await event.edit(
                    f"""**💻 Terminal**

`$ {command}`

❌ **Ошибка выполнения:**
```
{str(e)}
```"""
                    )
        client.add_event_handler(terminal_handler, events.NewMessage(
            outgoing=True))
