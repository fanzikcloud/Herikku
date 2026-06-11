import os
import tempfile
import asyncio
from core.base_module import Module


class TextToSpeechModule(Module):
    NAME = 'Text to Speech (Edge TTS)'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Озвучивает текст реалистичными голосами от Microsoft Edge с использованием библиотеки edge-tts'
    DEPENDENCIES = ['edge_tts']
    COMMANDS = {
        'tts': 'Озвучить текст на русском: .tts [текст] (или ответьте на сообщение)',
        'tts_en': 'Озвучить текст на английском: .tts_en [текст]',
        'tts_uk': 'Озвучить текст на украинском: .tts_uk [текст]',
        'tts_list': 'Список доступных голосов'
    }

    VOICES = {
        'ru': 'ru-RU-DmitryNeural',
        'ru_female': 'ru-RU-SvetlanaNeural',
        'en': 'en-US-GuyNeural',
        'en_female': 'en-US-JennyNeural',
        'uk': 'uk-UA-OstapNeural'
    }

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.install_package = install_package

        async def tts_handler(event):
            text = event.text or ''
            if not text.startswith(self.prefix):
                return

            cmd_parts = text[len(self.prefix):].split(maxsplit=1)
            if not cmd_parts:
                return
            
            cmd = cmd_parts[0].lower()
            if cmd not in ['tts', 'tts_en', 'tts_uk', 'tts_list']:
                return

            if cmd == 'tts_list':
                await event.edit(
                    "🗣 **Доступные голоса Edge TTS:**\n\n"
                    "• `.tts [текст]` — Русский (Дмитрий)\n"
                    "• `.tts -f [текст]` — Русский женский (Светлана)\n"
                    "• `.tts_en [текст]` — Английский (Гай)\n"
                    "• `.tts_en -f [текст]` — Английский женский (Дженни)\n"
                    "• `.tts_uk [текст]` — Украинский (Остап)\n\n"
                    "💡 *Вы также можете ответить на любое текстовое сообщение одной из команд, чтобы озвучить его.*"
                )
                return

            # Определяем голос
            voice = self.VOICES['ru']
            if cmd == 'tts_en':
                voice = self.VOICES['en']
            elif cmd == 'tts_uk':
                voice = self.VOICES['uk']

            # Извлечение текста
            tts_text = ""
            if len(cmd_parts) > 1:
                tts_text = cmd_parts[1].strip()

            # Обработка женского голоса
            if tts_text.startswith('-f ') or tts_text.startswith('--f ') or tts_text == '-f' or tts_text == '--f':
                if cmd == 'tts':
                    voice = self.VOICES['ru_female']
                elif cmd == 'tts_en':
                    voice = self.VOICES['en_female']
                
                if tts_text in ('-f', '--f'):
                    tts_text = ""
                else:
                    tts_text = tts_text.split(maxsplit=1)[1].strip()

            if not tts_text and event.is_reply:
                replied_msg = await event.get_reply_message()
                if replied_msg and replied_msg.text:
                    tts_text = replied_msg.text.strip()

            if not tts_text:
                await event.edit(
                    f'❌ Укажите текст после команды или ответьте на текстовое сообщение:\n'
                    f'`{self.prefix}{cmd} [текст]`\n'
                    f'💡 Для женского голоса: `{self.prefix}{cmd} -f [текст]`'
                )
                return

            await event.edit('🗣 Записываю голосовое...')

            try:
                # Динамически импортируем/устанавливаем библиотеку edge-tts
                try:
                    import edge_tts
                except ImportError:
                    await event.edit('📦 Установка зависимости `edge-tts`...')
                    try:
                        await self.install_package('edge-tts')
                        import edge_tts
                    except Exception as e:
                        await event.edit(f'❌ Не удалось установить edge-tts: {str(e)}')
                        return

                with tempfile.TemporaryDirectory() as temp_dir:
                    audio_path = os.path.join(temp_dir, 'voice.mp3')
                    
                    communicate = edge_tts.Communicate(tts_text, voice)
                    await communicate.save(audio_path)

                    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                        await event.edit('❌ Не удалось сгенерировать голосовое сообщение.')
                        return

                    # Отправляем аудио как голосовое сообщение
                    await event.delete()
                    await self.client.send_file(
                        event.chat_id,
                        audio_path,
                        voice_note=True,
                        reply_to=event.reply_to_msg_id
                    )

            except Exception as e:
                await event.edit(f'❌ Произошла ошибка при генерации TTS: {str(e)}')

        client.add_event_handler(tts_handler, events.NewMessage(outgoing=True))

    async def dispose(self):
        pass
