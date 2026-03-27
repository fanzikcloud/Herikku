from core.base_module import Module
from PIL import Image, ImageDraw, ImageFont
import io
import os


class QRCodeModule(Module):
    NAME = 'QR Code'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Генерация красивых QR-кодов с разными стилями'
    DEPENDENCIES = ['qrcode', 'Pil']
    COMMANDS = {'qr <текст>': 'Создать обычный QR-код', 'qrround <текст>':
        'QR-код с круглыми точками', 'qrcircle <текст>': 'QR-код с кругами',
        'qrgap <текст>': 'QR-код с промежутками', 'qrgrad <текст>':
        'QR-код с радиальным градиентом', 'qrsquare <текст>':
        'QR-код с квадратным градиентом', 'qrneon <текст>':
        'Неоновый QR-код', 'qrframe <текст>': 'QR-код с рамкой'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        print(f'📦 Проверка зависимостей для {self.NAME}...')
        try:
            import qrcode
            print('✅ qrcode уже установлен')
        except ImportError:
            print('⚠️  qrcode не найден, устанавливаю...')
            if await install_package('qrcode[pil]'):
                print('✅ qrcode установлен')
                import qrcode
            else:
                print('❌ Не удалось установить qrcode')
                return
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer, SquareModuleDrawer
        from qrcode.image.styles.colormasks import SolidFillColorMask, RadialGradiantColorMask, SquareGradiantColorMask

        def create_qr_base(data):
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants
                .ERROR_CORRECT_H, box_size=10, border=2)
            qr.add_data(data)
            qr.make(fit=True)
            return qr

        def add_frame(img, text, color=(0, 0, 0)):
            width, height = img.size
            new_width = width + 60
            new_height = height + 100
            new_img = Image.new('RGB', (new_width, new_height), 'white')
            draw = ImageDraw.Draw(new_img)
            for i in range(5):
                draw.rectangle([i, i, new_width - i - 1, new_height - i - 1
                    ], outline=color, width=1)
            new_img.paste(img, (30, 30))
            draw = ImageDraw.Draw(new_img)
            try:
                font = ImageFont.truetype('arial.ttf', 16)
            except:
                font = ImageFont.load_default()
            if len(text) > 30:
                text = text[:27] + '...'
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (new_width - text_width) // 2
            text_y = height + 50
            draw.text((text_x, text_y), text, fill=color, font=font)
            return new_img

        async def qr_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}qr '
                ):
                return
            data = event.text[len(f'{self.prefix}qr '):].strip()
            if not data:
                await event.edit(
                    f'**📱 QR Code**\n\nИспользование: `{self.prefix}qr <текст>`'
                    )
                return
            await event.edit('📱 Генерирую QR-код...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(fill_color='black', back_color='white')
                img = add_frame(img.convert('RGB'), data)
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""📱 **QR Code**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')

        async def qr_round_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}qrround '):
                return
            data = event.text[len(f'{self.prefix}qrround '):].strip()
            if not data:
                await event.edit(
                    f'**🔵 Round QR**\n\nИспользование: `{self.prefix}qrround <текст>`'
                    )
                return
            await event.edit('🔵 Генерирую круглый QR-код...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(image_factory=StyledPilImage,
                    module_drawer=RoundedModuleDrawer(), color_mask=
                    SolidFillColorMask(back_color=(255, 255, 255),
                    front_color=(0, 100, 200)))
                img = add_frame(img.convert('RGB'), data, (0, 100, 200))
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""🔵 **Round QR Code**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')

        async def qr_circle_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}qrcircle '):
                return
            data = event.text[len(f'{self.prefix}qrcircle '):].strip()
            if not data:
                await event.edit(
                    f"""**⭕ Circle QR**

Использование: `{self.prefix}qrcircle <текст>`"""
                    )
                return
            await event.edit('⭕ Генерирую QR-код с кругами...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(image_factory=StyledPilImage,
                    module_drawer=CircleModuleDrawer(), color_mask=
                    SolidFillColorMask(back_color=(255, 255, 255),
                    front_color=(200, 0, 100)))
                img = add_frame(img.convert('RGB'), data, (200, 0, 100))
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""⭕ **Circle QR Code**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')

        async def qr_gap_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}qrgap '):
                return
            data = event.text[len(f'{self.prefix}qrgap '):].strip()
            if not data:
                await event.edit(
                    f'**◻️ Gap QR**\n\nИспользование: `{self.prefix}qrgap <текст>`'
                    )
                return
            await event.edit('◻️ Генерирую QR-код с промежутками...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(image_factory=StyledPilImage,
                    module_drawer=GappedSquareModuleDrawer(), color_mask=
                    SolidFillColorMask(back_color=(255, 255, 255),
                    front_color=(100, 0, 200)))
                img = add_frame(img.convert('RGB'), data, (100, 0, 200))
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""◻️ **Gap QR Code**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')

        async def qr_grad_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}qrgrad '):
                return
            data = event.text[len(f'{self.prefix}qrgrad '):].strip()
            if not data:
                await event.edit(
                    f"""**🌈 Gradient QR**

Использование: `{self.prefix}qrgrad <текст>`"""
                    )
                return
            await event.edit('🌈 Генерирую градиентный QR-код...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(image_factory=StyledPilImage,
                    module_drawer=RoundedModuleDrawer(), color_mask=
                    RadialGradiantColorMask(back_color=(255, 255, 255),
                    center_color=(0, 150, 255), edge_color=(200, 0, 255)))
                img = add_frame(img.convert('RGB'), data, (100, 75, 255))
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""🌈 **Gradient QR Code**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')

        async def qr_square_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}qrsquare '):
                return
            data = event.text[len(f'{self.prefix}qrsquare '):].strip()
            if not data:
                await event.edit(
                    f"""**🔶 Square Gradient QR**

Использование: `{self.prefix}qrsquare <текст>`"""
                    )
                return
            await event.edit('🔶 Генерирую QR-код с квадратным градиентом...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(image_factory=StyledPilImage,
                    module_drawer=SquareModuleDrawer(), color_mask=
                    SquareGradiantColorMask(back_color=(255, 255, 255),
                    center_color=(255, 100, 0), edge_color=(255, 0, 100)))
                img = add_frame(img.convert('RGB'), data, (255, 50, 50))
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""🔶 **Square Gradient QR**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')

        async def qr_neon_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}qrneon '):
                return
            data = event.text[len(f'{self.prefix}qrneon '):].strip()
            if not data:
                await event.edit(
                    f'**💫 Neon QR**\n\nИспользование: `{self.prefix}qrneon <текст>`'
                    )
                return
            await event.edit('💫 Генерирую неоновый QR-код...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(image_factory=StyledPilImage,
                    module_drawer=CircleModuleDrawer(), color_mask=
                    RadialGradiantColorMask(back_color=(10, 10, 30),
                    center_color=(0, 255, 255), edge_color=(255, 0, 255)))
                img = add_frame(img.convert('RGB'), data, (0, 255, 255))
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""💫 **Neon QR Code**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')

        async def qr_frame_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}qrframe '):
                return
            data = event.text[len(f'{self.prefix}qrframe '):].strip()
            if not data:
                await event.edit(
                    f'**🖼 Frame QR**\n\nИспользование: `{self.prefix}qrframe <текст>`'
                    )
                return
            await event.edit('🖼 Генерирую QR-код с рамкой...')
            try:
                qr = create_qr_base(data)
                img = qr.make_image(image_factory=StyledPilImage,
                    module_drawer=RoundedModuleDrawer(), color_mask=
                    SolidFillColorMask(back_color=(255, 255, 255),
                    front_color=(50, 50, 50)))
                img = add_frame(img.convert('RGB'), data, (50, 50, 50))
                img.save('qr.png')
                await event.delete()
                await event.client.send_file(event.chat_id, 'qr.png',
                    caption=f"""🖼 **Frame QR Code**

{data[:100]}""")
                os.remove('qr.png')
            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)}')
        client.add_event_handler(qr_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(qr_round_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(qr_circle_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(qr_gap_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(qr_grad_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(qr_square_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(qr_neon_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(qr_frame_handler, events.NewMessage(
            outgoing=True))
