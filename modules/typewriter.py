from core.base_module import Module
import asyncio
import random


class TypewriterModule(Module):
    NAME = 'Typewriter'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Эффект печати текста с разными анимациями'
    DEPENDENCIES = []
    COMMANDS = {'print': 'Печать текста (.print <текст>)', 'type':
        'Печать с курсором (.type <текст>)', 'matrix':
        'Эффект Матрицы (.matrix <текст>)', 'wave':
        'Волновой эффект (.wave <текст>)', 'glitch':
        'Глитч эффект (.glitch <текст>)', 'fade':
        'Эффект появления (.fade <текст>)', 'reveal':
        'Постепенное раскрытие (.reveal <текст>)'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def print_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}print '):
                return
            text = event.text[len(f'{self.prefix}print '):]
            if not text:
                await event.edit(
                    f"""**⌨️ Typewriter**

Использование: `{self.prefix}print <текст>`"""
                    )
                return
            current_text = ''
            for char in text:
                current_text += char
                await event.edit(f'`{current_text}_`')
                await asyncio.sleep(0.1)
            await event.edit(f'`{current_text}`')

        async def type_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}type '):
                return
            text = event.text[len(f'{self.prefix}type '):]
            if not text:
                await event.edit(
                    f'**⌨️ Typewriter**\n\nИспользование: `{self.prefix}type <текст>`'
                    )
                return
            current_text = ''
            for char in text:
                current_text += char
                for _ in range(2):
                    await event.edit(f'`{current_text}█`')
                    await asyncio.sleep(0.05)
                    await event.edit(f'`{current_text}`')
                    await asyncio.sleep(0.05)
            await event.edit(f'`{current_text}`')

        async def matrix_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}matrix '):
                return
            text = event.text[len(f'{self.prefix}matrix '):]
            if not text:
                await event.edit(
                    f'**⌨️ Matrix**\n\nИспользование: `{self.prefix}matrix <текст>`'
                    )
                return
            chars = list(text)
            random_chars = ['█', '▓', '▒', '░', '▀', '▄', '▌', '▐', '■', '□']
            for i in range(len(text) + 5):
                display = ''
                for j, char in enumerate(chars):
                    if j < i:
                        display += char
                    else:
                        display += random.choice(random_chars)
                await event.edit(f'`{display}`')
                await asyncio.sleep(0.08)
            await event.edit(f'`{text}`')

        async def wave_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}wave '):
                return
            text = event.text[len(f'{self.prefix}wave '):]
            if not text:
                await event.edit(
                    f'**🌊 Wave**\n\nИспользование: `{self.prefix}wave <текст>`'
                    )
                return
            for i in range(len(text) + 1):
                display = ''
                for j, char in enumerate(text):
                    if j < i:
                        display += char
                    elif j == i:
                        display += f'**{char}**'
                    else:
                        display += '░'
                await event.edit(display)
                await asyncio.sleep(0.1)
            await event.edit(text)

        async def glitch_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}glitch '):
                return
            text = event.text[len(f'{self.prefix}glitch '):]
            if not text:
                await event.edit(
                    f'**⚡ Glitch**\n\nИспользование: `{self.prefix}glitch <текст>`'
                    )
                return
            glitch_chars = ['@', '#', '$', '%', '&', '*', '!', '?', '~']
            for _ in range(10):
                glitched = ''
                for char in text:
                    if random.random() < 0.3:
                        glitched += random.choice(glitch_chars)
                    else:
                        glitched += char
                await event.edit(f'`{glitched}`')
                await asyncio.sleep(0.05)
            for i in range(len(text)):
                display = text[:i + 1] + ''.join(random.choice(glitch_chars
                    ) for _ in range(len(text) - i - 1))
                await event.edit(f'`{display}`')
                await asyncio.sleep(0.08)
            await event.edit(f'`{text}`')

        async def fade_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}fade '):
                return
            text = event.text[len(f'{self.prefix}fade '):]
            if not text:
                await event.edit(
                    f'**✨ Fade**\n\nИспользование: `{self.prefix}fade <текст>`'
                    )
                return
            stages = ['░', '▒', '▓']
            for stage in stages:
                display = stage * len(text)
                await event.edit(f'`{display}`')
                await asyncio.sleep(0.15)
            for i in range(len(text) + 1):
                display = text[:i] + '▓' * (len(text) - i)
                await event.edit(f'`{display}`')
                await asyncio.sleep(0.08)
            await event.edit(f'`{text}`')

        async def reveal_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}reveal '):
                return
            text = event.text[len(f'{self.prefix}reveal '):]
            if not text:
                await event.edit(
                    f'**🎭 Reveal**\n\nИспользование: `{self.prefix}reveal <текст>`'
                    )
                return
            hidden = '█' * len(text)
            await event.edit(f'`{hidden}`')
            await asyncio.sleep(0.5)
            revealed = list('█' * len(text))
            positions = list(range(len(text)))
            random.shuffle(positions)
            for pos in positions:
                revealed[pos] = text[pos]
                await event.edit(f"`{''.join(revealed)}`")
                await asyncio.sleep(0.1)
            await event.edit(f'`{text}`')
        client.add_event_handler(print_handler, events.NewMessage(outgoing=
            True))
        client.add_event_handler(type_handler, events.NewMessage(outgoing=True)
            )
        client.add_event_handler(matrix_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(wave_handler, events.NewMessage(outgoing=True)
            )
        client.add_event_handler(glitch_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(fade_handler, events.NewMessage(outgoing=True)
            )
        client.add_event_handler(reveal_handler, events.NewMessage(outgoing
            =True))
