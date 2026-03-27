from core.base_module import Module
from PIL import Image, ImageDraw, ImageFont
import io
import os
import aiohttp


class WatermarkModule(Module):
    NAME = 'Watermark'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Добавляет водяной знак на изображения'
    DEPENDENCIES = ['Pillow']
    COMMANDS = {'wm':
        'Добавить водяной знак (.wm <текст> - ответить на фото)', 'wmset':
        'Настроить водяной знак (.wmset <параметр> <значение>)'}
    CONFIG_ICON = '💧'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_watermark':
            opacity = config.get('Watermark', 'opacity', fallback='128')
            position = config.get('Watermark', 'position', fallback=
                'bottom-right')
            font_size = config.get('Watermark', 'font_size', fallback='40')
            color = config.get('Watermark', 'color', fallback='white')
            text = '<b>💧 Watermark - Настройки</b>\n\n'
            text += f'🎨 <b>Прозрачность:</b> {opacity}/255\n'
            text += f'📍 <b>Позиция:</b> {position}\n'
            text += f'📏 <b>Размер шрифта:</b> {font_size}px\n'
            text += f'🎨 <b>Цвет:</b> {color}\n\n'
            text += '<b>Команды для настройки:</b>\n'
            text += (
                f'• <code>.wmset opacity &lt;0-255&gt;</code> - прозрачность\n'
                )
            text += (
                f'• <code>.wmset position &lt;позиция&gt;</code> - позиция\n')
            text += (
                f'• <code>.wmset size &lt;размер&gt;</code> - размер шрифта\n')
            text += (
                f'• <code>.wmset color &lt;цвет&gt;</code> - цвет текста\n\n')
            text += '<b>Доступные позиции:</b>\n'
            text += '• <code>top-left</code> - верх слева\n'
            text += '• <code>top-right</code> - верх справа\n'
            text += '• <code>bottom-left</code> - низ слева\n'
            text += '• <code>bottom-right</code> - низ справа\n'
            text += '• <code>center</code> - по центру\n\n'
            text += '<b>Цвета:</b> white, black, red, blue, green'
            buttons = [[Button.inline('◀️ К модулям', b'settings_modules')]]
            await event.edit(text, buttons=buttons)
        else:
            raise Exception('Not our callback')

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.config_path = config_path
        if not config.has_section('Watermark'):
            config.add_section('Watermark')
            config.set('Watermark', 'opacity', '180')
            config.set('Watermark', 'position', 'center')
            config.set('Watermark', 'font_size', '40')
            config.set('Watermark', 'color', 'white')
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
        self.font_path = 'Montserrat-Bold.ttf'
        if not os.path.exists(self.font_path):
            await self.download_font()
        self.colors = {'white': (255, 255, 255), 'black': (0, 0, 0), 'red':
            (255, 0, 0), 'blue': (0, 0, 255), 'green': (0, 255, 0),
            'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255,
            0, 255)}
        await self.setup_handlers(client, events)

    async def download_font(self):
        from core.text_formatter import TextFormatter
        print(TextFormatter.color('📥 Скачивание шрифта Montserrat...', 'cyan'))
        try:
            font_url = (
                'https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf'
                )
            async with aiohttp.ClientSession() as session:
                async with session.get(font_url) as response:
                    if response.status == 200:
                        font_data = await response.read()
                        with open(self.font_path, 'wb') as f:
                            f.write(font_data)
                        print(TextFormatter.color(
                            '✅ Шрифт Montserrat успешно скачан', 'green'))
                    else:
                        print(TextFormatter.color(
                            f'⚠️ Не удалось скачать шрифт (статус {response.status}), будет использован системный'
                            , 'yellow'))
        except Exception as e:
            print(TextFormatter.color(
                f'⚠️ Ошибка загрузки шрифта: {e}, будет использован системный',
                'yellow'))

    def add_watermark(self, image_bytes, text, opacity, position, font_size,
        color):
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        txt_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        try:
            if os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font_paths = ['C:/Windows/Fonts/arial.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/System/Library/Fonts/Helvetica.ttc']
                font = None
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        break
                if not font:
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        margin = 20
        if position == 'top-left':
            x, y = margin, margin
        elif position == 'top-right':
            x, y = image.width - text_width - margin, margin
        elif position == 'bottom-left':
            x, y = margin, image.height - text_height - margin
        elif position == 'bottom-right':
            x, y = (image.width - text_width - margin, image.height -
                text_height - margin)
        elif position == 'center':
            x, y = (image.width - text_width) // 2, (image.height - text_height
                ) // 2
        else:
            x, y = (image.width - text_width - margin, image.height -
                text_height - margin)
        text_color = color + (opacity,)
        draw.text((x, y), text, font=font, fill=text_color)
        watermarked = Image.alpha_composite(image, txt_layer)
        watermarked = watermarked.convert('RGB')
        output = io.BytesIO()
        watermarked.save(output, format='JPEG', quality=95)
        output.seek(0)
        output.name = 'watermarked.jpg'
        return output

    async def setup_handlers(self, client, events):

        async def wm_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}wm'):
                return
            if not event.reply_to_msg_id:
                await event.edit(
                    f"""**💧 Добавление водяного знака**

Ответьте этой командой на фото:
`{self.prefix}wm <текст>`

**Пример:**
`{self.prefix}wm @username`"""
                    )
                return
            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.edit('❌ Укажите текст для водяного знака')
                return
            watermark_text = parts[1]
            reply_msg = await event.get_reply_message()
            if not reply_msg.photo:
                await event.edit('❌ Сообщение не содержит фото')
                return
            try:
                await event.edit('⏳ Обработка изображения...')
                photo_bytes = await reply_msg.download_media(file=bytes)
                opacity = int(self.config.get('Watermark', 'opacity',
                    fallback='128'))
                position = self.config.get('Watermark', 'position',
                    fallback='bottom-right')
                font_size = int(self.config.get('Watermark', 'font_size',
                    fallback='40'))
                color_name = self.config.get('Watermark', 'color', fallback
                    ='white')
                color = self.colors.get(color_name, (255, 255, 255))
                watermarked_image = self.add_watermark(photo_bytes,
                    watermark_text, opacity, position, font_size, color)
                await event.delete()
                await self.client.send_file(event.chat_id,
                    watermarked_image, force_document=False, attributes=[])
            except Exception as e:
                await event.edit(f'❌ Ошибка обработки: {str(e)}')

        async def wmset_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}wmset'):
                return
            parts = event.text.split(maxsplit=2)
            if len(parts) < 3:
                await event.edit(
                    f"""**⚙️ Настройка водяного знака**

**Использование:**
`{self.prefix}wmset <параметр> <значение>`

**Параметры:**
• `opacity` - прозрачность (0-255)
• `position` - позиция
• `size` - размер шрифта
• `color` - цвет текста

**Примеры:**
`{self.prefix}wmset opacity 200`
`{self.prefix}wmset position center`
`{self.prefix}wmset size 50`
`{self.prefix}wmset color red`"""
                    )
                return
            param = parts[1].lower()
            value = parts[2]
            try:
                if param == 'opacity':
                    opacity = int(value)
                    if opacity < 0 or opacity > 255:
                        await event.edit(
                            '❌ Прозрачность должна быть от 0 до 255')
                        return
                    self.config.set('Watermark', 'opacity', str(opacity))
                    await event.edit(f'✅ Прозрачность установлена: {opacity}')
                elif param == 'position':
                    valid_positions = ['top-left', 'top-right',
                        'bottom-left', 'bottom-right', 'center']
                    if value not in valid_positions:
                        await event.edit(
                            f"❌ Неверная позиция. Доступные: {', '.join(valid_positions)}"
                            )
                        return
                    self.config.set('Watermark', 'position', value)
                    await event.edit(f'✅ Позиция установлена: {value}')
                elif param == 'size':
                    size = int(value)
                    if size < 10 or size > 200:
                        await event.edit('❌ Размер должен быть от 10 до 200')
                        return
                    self.config.set('Watermark', 'font_size', str(size))
                    await event.edit(f'✅ Размер шрифта установлен: {size}px')
                elif param == 'color':
                    if value not in self.colors:
                        await event.edit(
                            f"❌ Неверный цвет. Доступные: {', '.join(self.colors.keys())}"
                            )
                        return
                    self.config.set('Watermark', 'color', value)
                    await event.edit(f'✅ Цвет установлен: {value}')
                else:
                    await event.edit(f'❌ Неизвестный параметр: {param}')
                    return
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
            except ValueError:
                await event.edit('❌ Неверное значение параметра')
        client.add_event_handler(wm_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(wmset_handler, events.NewMessage(outgoing=
            True))
