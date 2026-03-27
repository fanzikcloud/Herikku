from core.base_module import Module
import speech_recognition as sr
import os
import tempfile


class VoiceToTextModule(Module):
    NAME = 'Voice to Text'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Транскрибирует голосовые сообщения в текст'
    DEPENDENCIES = []
    COMMANDS = {'voice':
        'Транскрибировать голосовое сообщение (ответьте на голосовое)', 'v':
        'Транскрибировать голосовое (короткая команда)'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def transcribe_voice_handler(event):
            if not event.text or not event.text.startswith((
                f'{self.prefix}voice', f'{self.prefix}v ')):
                if event.text == f'{self.prefix}v':
                    pass
                elif not event.text.startswith(f'{self.prefix}voice'):
                    return
            if not event.is_reply:
                await event.edit(
                    '❌ Ответьте этой командой на голосовое сообщение')
                return
            replied_msg = await event.get_reply_message()
            if not replied_msg.voice and not replied_msg.video_note:
                await event.edit('❌ Это не голосовое сообщение')
                return
            await event.edit('🎧 Слушаю...')
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    voice_path = os.path.join(temp_dir, 'voice.ogg')
                    await replied_msg.download_media(voice_path)
                    wav_path = os.path.join(temp_dir, 'voice.wav')
                    try:
                        import soundfile as sf
                        data, samplerate = sf.read(voice_path)
                        sf.write(wav_path, data, samplerate, format='WAV')
                    except ImportError:
                        await event.edit(
                            '❌ Установите зависимость:\n`pip install soundfile`'
                            )
                        return
                    except Exception as e:
                        await event.edit(
                            f'❌ Ошибка конвертации аудио: {str(e)}')
                        return
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        recognizer.adjust_for_ambient_noise(source,
                            duration=0.5)
                        audio_data = recognizer.record(source)
                        try:
                            text = recognizer.recognize_google(audio_data,
                                language='ru-RU')
                        except sr.UnknownValueError:
                            try:
                                text = recognizer.recognize_google(audio_data,
                                    language='en-US')
                            except sr.UnknownValueError:
                                await event.edit(
                                    """❌ Не удалось распознать речь
💡 Попробуйте с более четким голосовым"""
                                    )
                                return
                        except sr.RequestError:
                            await event.edit(
                                """❌ Ошибка сервиса распознавания
💡 Проверьте интернет соединение"""
                                )
                            return
                    sender = await replied_msg.get_sender()
                    sender_name = (sender.first_name if sender.first_name else
                        'Неизвестно')
                    try:
                        if replied_msg.voice:
                            duration = replied_msg.voice.duration
                        elif replied_msg.video_note:
                            duration = replied_msg.video_note.duration
                        else:
                            duration = '?'
                    except:
                        duration = '?'
                    result = f'🎤 **Текст из голосового:**\n\n'
                    result += f'_{text}_\n\n'
                    result += f'👤 От: {sender_name}\n'
                    result += f'⏱ Длительность: {duration} сек'
                    await event.edit(result)
            except Exception as e:
                import traceback
                traceback.print_exc()
                await event.edit(f'❌ Ошибка: {str(e)}')
        client.add_event_handler(transcribe_voice_handler, events.
            NewMessage(outgoing=True))
