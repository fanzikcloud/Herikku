import io
import asyncio
import aiohttp
from core.base_module import Module


class TikTokModule(Module):
    NAME = 'TikTok'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Скачивание TikTok видео по ссылке (без водяного знака)'
    DEPENDENCIES = []
    COMMANDS = {
        'tt': 'Скачать TikTok видео (.tt <ссылка>)',
        'ttinfo': 'Информация о TikTok видео (.ttinfo <ссылка>)',
    }
    CONFIG_ICON = '🎵'

    async def init(self, client, command_prefix, events, load_module,
                   loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        # Переключаемся на надежный бесплатный API TikWM
        self.api_base = 'https://tikwm.com/api/'
        await self.setup_handlers(client, events)

    def _clean_url(self, url: str) -> str:
        import re
        import html
        url = html.unescape(url)
        url = re.sub(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>.*?</a>', r'\1', url, flags=re.IGNORECASE | re.DOTALL)
        url = re.sub(r'<[^>]+>', '', url)
        return url.strip()

    async def _get_video_data(self, url: str) -> dict:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            params = {'url': url}
            async with session.get(self.api_base, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f'API вернул ошибку: HTTP {resp.status}\n{text[:200]}')

                result = await resp.json()

                if not result or result.get('code') != 0:
                    error_msg = result.get('msg', 'Неизвестная ошибка парсинга URL')
                    raise Exception(f'API ошибка: {error_msg}')

                return result.get('data', {})

    async def _download_video_bytes(self, video_url: str) -> bytes:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status != 200:
                    raise Exception(f'Ошибка скачивания: HTTP {resp.status}')

                return await resp.read()

    async def setup_handlers(self, client, events):

        async def tt_handler(event):
            if not event.text:
                return
            cmd = event.text.split()[0]
            if cmd != f'{self.prefix}tt':
                return

            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.edit(
                    f'**🎵 TikTok Downloader**\n\n'
                    f'Использование: `{self.prefix}tt <ссылка>`\n\n'
                    f'Поддерживаются:\n'
                    f'• https://www.tiktok.com/@user/video/123\n'
                    f'• https://vt.tiktok.com/ZSxxxxxx/\n'
                    f'• https://vm.tiktok.com/ZSxxxxxx/\n'
                    f'• Douyin ссылки'
                )
                return

            url = self._clean_url(parts[1])

            if 'tiktok.com' not in url and 'douyin.com' not in url:
                await event.edit('❌ Укажите корректную ссылку на TikTok/Douyin видео')
                return

            await event.edit('⏳ Получаю данные...')

            try:
                video_data = await self._get_video_data(url)

                # У TikWM URL видео без ватермарка лежит в data['play']
                video_url = video_data.get('play')
                if not video_url:
                    await event.edit('❌ Не удалось получить ссылку на видео')
                    return

                await event.edit('⏳ Скачиваю видео...')
                video_bytes = await self._download_video_bytes(video_url)

                if len(video_bytes) < 10000:
                    raise Exception('Файл слишком маленький')

                buf = io.BytesIO(video_bytes)
                buf.name = 'tiktok.mp4'

                author = video_data.get('author', {})
                author_name = author.get('nickname', '') if isinstance(author, dict) else ''
                author_username = author.get('unique_id', '') if isinstance(author, dict) else ''

                desc = video_data.get('title', '')
                duration = video_data.get('duration', 0)

                caption = f'🎵 **TikTok**\n'
                if desc:
                    caption += f'📝 {desc[:100]}\n'
                if author_name:
                    caption += f'👤 {author_name}'
                    if author_username:
                        caption += f' (@{author_username})'
                    caption += '\n'
                if duration:
                    mins, secs = divmod(int(duration), 60)
                    caption += f'⏱ {mins}:{secs:02d}\n'

                caption += f'\n💾 {len(video_bytes) / (1024*1024):.2f} MB'
                caption += '\n✨ Без водяного знака'

                await event.delete()
                await self.client.send_file(
                    event.chat_id,
                    buf,
                    caption=caption,
                    supports_streaming=True
                )

            except Exception as e:
                await event.edit(f'❌ Не удалось скачать видео:\n{str(e)[:200]}')

        async def ttinfo_handler(event):
            if not event.text or not event.text.startswith(f'{self.prefix}ttinfo'):
                return

            parts = event.text.split(maxsplit=1)
            if len(parts) < 2:
                await event.edit(f'**ℹ️ TikTok Info**\n\nИспользование: `{self.prefix}ttinfo <ссылка>`')
                return

            url = self._clean_url(parts[1])

            if 'tiktok.com' not in url and 'douyin.com' not in url:
                await event.edit('❌ Укажите корректную ссылку на TikTok/Douyin видео')
                return

            await event.edit('⏳ Получаю информацию...')

            try:
                data = await self._get_video_data(url)

                author = data.get('author', {})
                author_name = author.get('nickname', 'Неизвестен') if isinstance(author, dict) else 'Неизвестен'
                author_username = author.get('unique_id', '') if isinstance(author, dict) else ''

                desc = data.get('title', 'Нет описания')

                play_count = data.get('play_count', 0)
                like_count = data.get('digg_count', 0)
                comment_count = data.get('comment_count', 0)
                share_count = data.get('share_count', 0)

                duration = data.get('duration', 0)
                mins, secs = divmod(int(duration), 60)

                music_info = data.get('music_info', {})
                music_title = music_info.get('title', 'Нет музыки') if isinstance(music_info, dict) else 'Нет музыки'

                text = f'**🎵 TikTok — Информация**\n\n'
                text += f'👤 **Автор:** {author_name}'
                if author_username:
                    text += f' (@{author_username})'
                text += '\n'
                text += f'📝 **Описание:** {desc[:100]}\n'
                text += f'⏱ **Длительность:** {mins}:{secs:02d}\n'
                if music_title and music_title != 'Нет музыки':
                    text += f'🎵 **Музыка:** {music_title}\n'

                if any([play_count, like_count, comment_count, share_count]):
                    text += f'\n📊 **Статистика:**\n'
                    if play_count:
                        text += f'▶️ Просмотры: {play_count:,}\n'
                    if like_count:
                        text += f'❤️ Лайки: {like_count:,}\n'
                    if comment_count:
                        text += f'💬 Комментарии: {comment_count:,}\n'
                    if share_count:
                        text += f'🔄 Репосты: {share_count:,}'

                await event.edit(text)

            except Exception as e:
                await event.edit(f'❌ Ошибка: {str(e)[:200]}')

        client.add_event_handler(tt_handler, events.NewMessage(outgoing=True))
        client.add_event_handler(ttinfo_handler, events.NewMessage(outgoing=True))
