from core.base_module import Module
import os
import io
import json
import asyncio
import aiohttp
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class LastfyModule(Module):
    NAME = 'Lastfy'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Показывает красивую карточку прослушиваемого трека из Last.fm с обложкой и реальной длительностью'
    DEPENDENCIES = ['Pillow', 'aiohttp']
    COMMANDS = {
        'lastfy': 'Показать прослушиваемый трек из Last.fm на красивой картинке',
        'setlastfm <username> [api_key]': 'Установить юзернейм Last.fm и необязательный API-ключ'
    }
    CONFIG_ICON = '🎵'

    # Дефолтный публичный API-ключ Last.fm
    DEFAULT_API_KEY = 'b25b959554ed76058ac220b7b2e0a026'

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config
        self.config_path = config_path

        if not config.has_section('Lastfm'):
            config.add_section('Lastfm')
            config.set('Lastfm', 'username', '')
            config.set('Lastfm', 'api_key', self.DEFAULT_API_KEY)
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)

        self.font_path = 'Montserrat-Bold.ttf'

        async def lastfy_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}lastfy'):
                return

            username = self.config.get('Lastfm', 'username', fallback='').strip()
            api_key = self.config.get('Lastfm', 'api_key', fallback=self.DEFAULT_API_KEY).strip()

            if not username:
                await event.edit(
                    f"<b>⚠️ Настройте аккаунт Last.fm!</b>\n\n"
                    f"Введите: <code>{self.prefix}setlastfm &lt;ваш_юзернейм&gt;</code>\n"
                    f"<i>Пример:</i> <code>{self.prefix}setlastfm fanzikcloud</code>"
                )
                return

            await event.edit("<b>🎵 Получаю статус прослушивания из Last.fm...</b>")

            try:
                # 1. Запрос к API Last.fm (getrecenttracks)
                url = "http://ws.audioscrobbler.com/2.0/"
                params = {
                    'method': 'user.getrecenttracks',
                    'user': username,
                    'api_key': api_key,
                    'limit': 1,
                    'format': 'json'
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, timeout=10) as response:
                        if response.status != 200:
                            await event.edit(
                                f"<b>❌ Ошибка Last.fm API:</b> HTTP {response.status}\n"
                                f"https://www.last.fm/api/account/create"
                            )
                            return
                        data = await response.json()

                recent_tracks = data.get('recenttracks', {}).get('track', [])
                if not recent_tracks:
                    await event.edit("<b>❌ В истории Last.fm нет треков!</b>")
                    return

                track_data = recent_tracks[0] if isinstance(recent_tracks, list) else recent_tracks
                
                # Проверяем, играет ли трек сейчас
                is_now_playing = False
                if '@attr' in track_data:
                    is_now_playing = track_data['@attr'].get('nowplaying') == 'true'

                track_name = track_data.get('name', 'Неизвестный трек')
                artist_name = track_data.get('artist', {}).get('#text', 'Неизвестный исполнитель')
                album_name = track_data.get('album', {}).get('#text', '')

                # Ищем штамп времени начала скроблинга для играющего сейчас или недавно завершенного трека
                start_timestamp = 0
                if 'date' in track_data:
                    start_timestamp = int(track_data['date'].get('uts', '0'))

                # 2. Получение детальной информации о треке (для реальной длительности)
                duration_sec = 0
                try:
                    info_params = {
                        'method': 'track.getInfo',
                        'api_key': api_key,
                        'artist': artist_name,
                        'track': track_name,
                        'username': username,
                        'format': 'json'
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=info_params, timeout=5) as info_resp:
                            if info_resp.status == 200:
                                info_data = await info_resp.json()
                                dur_str = info_data.get('track', {}).get('duration', '0')
                                if dur_str and dur_str.isdigit():
                                    duration_sec = int(int(dur_str) / 1000)
                except Exception as info_err:
                    print(f"Error getting track info: {info_err}")

                # Ищем самую большую обложку альбома
                images = track_data.get('image', [])
                cover_url = ""
                if images:
                    for img in reversed(images):
                        if img.get('#text'):
                            cover_url = img.get('#text')
                            break

                # 3. Скачивание обложки
                cover_bytes = None
                if cover_url:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(cover_url, timeout=5) as img_resp:
                                if img_resp.status == 200:
                                    cover_bytes = await img_resp.read()
                    except:
                        pass

                # 4. Отрисовка карточки через Pillow
                await event.edit("<b>🎨 Отрисовываю карточку трека...</b>")
                card_image = await asyncio.to_thread(
                    self.draw_track_card, track_name, artist_name, album_name, cover_bytes, is_now_playing, duration_sec, start_timestamp
                )

                # 5. Отправка карточки
                await event.delete()
                await self.client.send_file(
                    event.chat_id,
                    card_image,
                    caption=f"🎵 <b>{artist_name}</b> — <i>{track_name}</i>",
                    reply_to=event.reply_to_msg_id
                )

            except Exception as e:
                await event.edit(f"<b>❌ Ошибка генерации Lastfy:</b>\n<code>{str(e)}</code>")

        async def setlastfm_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}setlastfm'):
                return
            parts = event.text.split(maxsplit=2)
            if len(parts) < 2:
                await event.edit(
                    f"<b>🔧 Настройка аккаунта Last.fm</b>\n\n"
                    f"Использование: <code>{self.prefix}setlastfm &lt;юзернейм&gt; [api_key]</code>"
                )
                return

            username = parts[1].strip()
            api_key = parts[2].strip() if len(parts) > 2 else self.DEFAULT_API_KEY

            self.config.set('Lastfm', 'username', username)
            self.config.set('Lastfm', 'api_key', api_key)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)

            await event.edit(
                f"<b>✅ Аккаунт Last.fm успешно привязан!</b>\n\n"
                f"👤 Юзернейм: <code>{username}</code>\n"
                f"🔑 API-ключ: <code>{api_key[:6]}...{api_key[-6:] if api_key != self.DEFAULT_API_KEY else 'Default'}</code>\n\n"
                f"<i>Введите <code>{self.prefix}lastfy</code> для проверки!</i>"
            )

        client.add_event_handler(lastfy_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(setlastfm_handler, events.NewMessage(outgoing=True))

    def draw_track_card(self, track, artist, album, cover_bytes, is_now_playing, duration_sec, start_timestamp):
        # Премиальный ультраминималистичный Spotify-дизайн
        # Размеры карточки с закруглением границ всей картинки
        width, height = 820, 260
        
        # Создаем прозрачное полотно для поддержки закругления углов у всей карточки
        card = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card)

        # Рисуем саму карточку с очень мягким темным матовым градиентом/цветом (Spotify Dark)
        bg_color = (18, 18, 18, 255) # Spotify Black
        draw.rounded_rectangle([0, 0, width, height], radius=24, fill=bg_color)

        # 1. Загрузка шрифтов
        try:
            if os.path.exists(self.font_path):
                font_title = ImageFont.truetype(self.font_path, 30)   # Крупный заголовок
                font_artist = ImageFont.truetype(self.font_path, 21)  # Обычный исполнитель
                font_sub = ImageFont.truetype(self.font_path, 12)     # Маленькие метки
                font_time = ImageFont.truetype(self.font_path, 13)    # Мягкие тайминги
            else:
                font_title = font_artist = font_sub = font_time = ImageFont.load_default()
        except:
            font_title = font_artist = font_sub = font_time = ImageFont.load_default()

        # 2. Отрисовка обложки альбома (с левым отступом и мягкими тенями)
        cover_size = 200
        cover_x, cover_y = 30, 30
        
        if cover_bytes:
            try:
                cover_img = Image.open(io.BytesIO(cover_bytes)).convert('RGBA')
                cover_img = cover_img.resize((cover_size, cover_size), Image.Resampling.LANCZOS)
                
                # Мягкое скругление краев обложки
                mask = Image.new('L', (cover_size, cover_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle([0, 0, cover_size, cover_size], radius=16, fill=255)
                
                card.paste(cover_img, (cover_x, cover_y), mask=mask)
            except:
                cover_bytes = None

        if not cover_bytes:
            # Премиальный монохромный градиент-заглушка для обложки
            placeholder = Image.new('RGBA', (cover_size, cover_size), (28, 28, 28, 255))
            p_draw = ImageDraw.Draw(placeholder)
            p_draw.rounded_rectangle([0, 0, cover_size, cover_size], radius=16, fill=(33, 33, 33, 255), outline=(45, 45, 45, 255), width=2)
            # Минималистичная иконка ноты
            p_draw.ellipse([70, 70, 130, 130], fill=(48, 48, 48, 255))
            card.paste(placeholder, (cover_x, cover_y))

        # 3. Текстовая информация (Сдвигаем вправо)
        text_x = 260
        
        # Эстетичный анимированный индикатор активности
        if is_now_playing:
            status_text = "●  NOW PLAYING"
            status_color = (30, 215, 96, 255) # Зеленый Spotify Accent
        else:
            status_text = "●  LAST PLAYED"
            status_color = (170, 170, 170, 255) # Благородный серый
            
        draw.text((text_x, 35), status_text, font=font_sub, fill=status_color)

        # Ограничиваем длину трека для идеального минималистичного размещения
        if len(track) > 30:
            track = track[:27] + "..."
        draw.text((text_x, 58), track, font=font_title, fill=(255, 255, 255, 255))

        # Исполнитель (и альбом) в нежном сером цвете
        full_artist = artist
        if album:
            full_artist += f" • {album}"
        if len(full_artist) > 40:
            full_artist = full_artist[:37] + "..."
        draw.text((text_x, 102), full_artist, font=font_artist, fill=(160, 160, 160, 255))

        # 4. Премиальный тонкий прогресс-бар
        bar_x = text_x
        bar_y = 175
        bar_width = 530
        bar_height = 4 # Еще тоньше и элегантнее

        # Полупрозрачная подложка прогресс-бара
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], radius=2, fill=(40, 40, 40, 255))

        total_sec = duration_sec if duration_sec > 0 else 180

        if is_now_playing:
            now_ts = int(time.time())
            if start_timestamp > 0:
                elapsed_sec = now_ts - start_timestamp
                if elapsed_sec > total_sec:
                    elapsed_sec = elapsed_sec % total_sec
            else:
                hash_val = abs(hash(track + artist))
                progress_pct = (hash_val % 45 + 30) / 100.0
                elapsed_sec = int(total_sec * progress_pct)

            current_sec = elapsed_sec
            progress_pct = current_sec / total_sec
            if progress_pct > 1.0:
                progress_pct = 1.0
                current_sec = total_sec

            t_min, t_sec = divmod(total_sec, 60)
            c_min, c_sec = divmod(current_sec, 60)
            
            time_current = f"{c_min}:{c_sec:02d}"
            time_total = f"{t_min}:{t_sec:02d}"
        else:
            progress_pct = 1.0
            time_current = "Конец"
            time_total = "трека"

        # Заполненная активная часть прогресс-бара
        active_width = int(bar_width * progress_pct)
        if active_width > 0:
            active_color = (30, 215, 96, 255) if is_now_playing else (100, 100, 100, 255)
            draw.rounded_rectangle([bar_x, bar_y, bar_x + active_width, bar_y + bar_height], radius=2, fill=active_color)
            
            # Эстетичный маленький ползунок (кноб)
            if is_now_playing:
                knob_x = bar_x + active_width
                knob_r = 5
                draw.ellipse([knob_x - knob_r, bar_y + 2 - knob_r, knob_x + knob_r, bar_y + 2 + knob_r], fill=(255, 255, 255, 255))

        # Тайминги (приглушенный цвет, ровный правый край)
        draw.text((bar_x, bar_y + 16), time_current, font=font_time, fill=(120, 120, 120, 255))
        
        try:
            bbox = draw.textbbox((0, 0), time_total, font=font_time)
            text_w = bbox[2] - bbox[0]
        except:
            text_w = 30
        draw.text((bar_x + bar_width - text_w, bar_y + 16), time_total, font=font_time, fill=(120, 120, 120, 255))

        # 5. Сохранение в PNG с поддержкой сглаженного альфа-канала (прозрачности краев)
        output = io.BytesIO()
        card.save(output, format='PNG')
        output.seek(0)
        output.name = 'lastfy.png'
        return output
