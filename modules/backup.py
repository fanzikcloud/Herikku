from core.base_module import Module
from core.herikku_archive import HerikkunArchive
from core.progress_bar import ProgressBar
import os
import glob
from datetime import datetime


class BackupModule(Module):
    NAME = 'Backup'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Резервное копирование конфигов и сессий в формате .herikku'
    DEPENDENCIES = ['cryptography']
    COMMANDS = {'backup': 'Создать резервную копию (.backup [пароль])',
        'restore':
        'Восстановить из резервной копии (ответить на .herikku файл)',
        'backuplist': 'Список файлов в архиве (ответить на .herikku файл)',
        'backupinfo': 'Информация о текущих данных'}
    CONFIG_ICON = '💾'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_backup':
            text = '<b>💾 Backup - Резервное копирование</b>\n\n'
            text += '<b>Формат архива:</b> <code>.herikku</code>\n'
            text += '🔒 Защищен шифрованием\n'
            text += '🗜 Сжатие данных\n'
            text += '🚫 Нельзя открыть обычными архиваторами\n\n'
            text += '<b>Команды:</b>\n'
            text += '• <code>.backup</code> - создать backup\n'
            text += (
                '• <code>.backup &lt;пароль&gt;</code> - backup с паролем\n')
            text += (
                '• <code>.restore</code> - восстановить (ответить на файл)\n')
            text += '• <code>.backuplist</code> - список файлов в архиве\n'
            text += '• <code>.backupinfo</code> - информация о данных\n\n'
            text += '<b>Что сохраняется:</b>\n'
            text += '✅ Все конфиги (config*.ini)\n'
            text += '✅ Все сессии (*.session)\n'
            text += '✅ Медиа файлы модулей\n'
            text += '✅ Метаданные\n\n'
            text += '⚠️ Храните backup в безопасном месте!'
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

        async def backup_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}backup'):
                return
            if event.text.startswith(f'{self.prefix}backuplist'
                ) or event.text.startswith(f'{self.prefix}backupinfo'):
                return
            parts = event.text.split(maxsplit=1)
            password = parts[1] if len(parts) > 1 else None
            msg = await event.edit('🔍 Сканирование файлов...')
            try:
                files_to_backup = {}
                config_files = glob.glob('config*.ini')
                for config_file in config_files:
                    files_to_backup[config_file] = config_file
                session_files = glob.glob('*.session')
                for session_file in session_files:
                    files_to_backup[session_file] = session_file
                session_journals = glob.glob('*.session-journal')
                for journal_file in session_journals:
                    files_to_backup[journal_file] = journal_file
                media_files = glob.glob('info_media_*.*')
                for media_file in media_files:
                    files_to_backup[media_file] = media_file
                if not files_to_backup:
                    await msg.edit('⚠️ Нет файлов для резервного копирования')
                    return
                total_files = len(files_to_backup)
                progress = ProgressBar(msg, total_files, prefix=
                    '💾 <b>Создание резервной копии</b>', suffix=
                    f'Файлов: {total_files}')
                await progress.update(0, 'Подготовка архива...')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f'herikku_backup_{timestamp}.herikku'
                me = await self.client.get_me()
                metadata = {'user_id': me.id, 'username': me.username or
                    'unknown', 'first_name': me.first_name, 'timestamp':
                    timestamp, 'files_count': total_files, 'has_password': 
                    password is not None}
                await progress.update(total_files // 4,
                    'Сжатие и шифрование...')
                archive = HerikkunArchive(password=password)
                success = archive.create(backup_filename, files_to_backup,
                    metadata)
                if not success:
                    await msg.edit('❌ Ошибка создания архива')
                    return
                await progress.update(total_files // 2,
                    'Подготовка к отправке...')
                file_size = os.path.getsize(backup_filename)
                file_size_mb = file_size / (1024 * 1024)
                await progress.update(total_files * 3 // 4, 'Отправка файла...'
                    )
                caption = f'**💾 Резервная копия Herikku**\n\n'
                caption += (
                    f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                    )
                caption += f'👤 Аккаунт: {me.first_name}'
                if me.username:
                    caption += f' (@{me.username})'
                caption += f'\n📦 Файлов: {total_files}\n'
                caption += f'💿 Размер: {file_size_mb:.2f} MB\n'
                if password:
                    caption += f'🔐 Защищен паролем\n'
                caption += f'\n⚠️ Храните в безопасном месте!'
                await self.client.send_file('me', backup_filename, caption=
                    caption)
                await progress.finish(
                    '✅ Резервная копия создана и отправлена в Избранное!')
                os.remove(backup_filename)
            except Exception as e:
                await msg.edit(
                    f'❌ Ошибка создания backup:\n<code>{str(e)}</code>')
                import traceback
                traceback.print_exc()

        async def restore_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}restore'):
                return
            if not event.is_reply:
                await event.edit(
                    f"""**💾 Восстановление из backup**

Ответьте этой командой на файл `.herikku`

**Использование:**
• `{self.prefix}restore` - без пароля
• `{self.prefix}restore <пароль>` - с паролем"""
                    )
                return
            parts = event.text.split(maxsplit=1)
            password = parts[1] if len(parts) > 1 else None
            reply_msg = await event.get_reply_message()
            if not reply_msg.document:
                await event.edit('❌ Сообщение не содержит файл')
                return
            filename = reply_msg.file.name
            if not filename or not filename.endswith('.herikku'):
                await event.edit('❌ Файл должен иметь расширение .herikku')
                return
            msg = await event.edit('📥 Скачивание архива...')
            try:
                temp_archive = f'temp_{filename}'
                await reply_msg.download_media(temp_archive)
                await msg.edit('🔓 Расшифровка и распаковка...')
                archive = HerikkunArchive(password=password)
                info = archive.list_contents(temp_archive)
                if not info:
                    await msg.edit(
                        '❌ Не удалось прочитать архив. Проверьте пароль.')
                    os.remove(temp_archive)
                    return
                total_files = len(info['files'])
                progress = ProgressBar(msg, total_files, prefix=
                    '💾 <b>Восстановление из backup</b>', suffix=
                    f'Файлов: {total_files}')
                await progress.update(0, 'Извлечение файлов...')
                result = archive.extract(temp_archive, '.')
                if not result:
                    await msg.edit('❌ Ошибка извлечения файлов')
                    os.remove(temp_archive)
                    return
                await progress.update(total_files, 'Очистка...')
                os.remove(temp_archive)
                restored_text = '✅ Восстановлено:\n'
                for file_info in result['files'][:10]:
                    restored_text += (
                        f"• {os.path.basename(file_info['path'])}\n")
                if len(result['files']) > 10:
                    restored_text += (
                        f"• ... и еще {len(result['files']) - 10} файлов\n")
                await progress.finish(
                    f"""✅ <b>Backup восстановлен!</b>

{restored_text}
⚠️ Перезапустите бота для применения изменений"""
                    )
            except Exception as e:
                await msg.edit(
                    f'❌ Ошибка восстановления:\n<code>{str(e)}</code>')
                if os.path.exists(temp_archive):
                    os.remove(temp_archive)
                import traceback
                traceback.print_exc()

        async def backuplist_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}backuplist'):
                return
            if not event.is_reply:
                await event.edit(
                    f"""**💾 Список файлов в архиве**

Ответьте этой командой на файл `.herikku`"""
                    )
                return
            parts = event.text.split(maxsplit=1)
            password = parts[1] if len(parts) > 1 else None
            reply_msg = await event.get_reply_message()
            if not reply_msg.document:
                await event.edit('❌ Сообщение не содержит файл')
                return
            filename = reply_msg.file.name
            if not filename or not filename.endswith('.herikku'):
                await event.edit('❌ Файл должен иметь расширение .herikku')
                return
            msg = await event.edit('📥 Анализ архива...')
            try:
                temp_archive = f'temp_{filename}'
                await reply_msg.download_media(temp_archive)
                archive = HerikkunArchive(password=password)
                info = archive.list_contents(temp_archive)
                os.remove(temp_archive)
                if not info:
                    await msg.edit(
                        '❌ Не удалось прочитать архив. Проверьте пароль.')
                    return
                text = f'**💾 Содержимое архива**\n\n'
                text += f"📅 Создан: {info['created']}\n"
                text += f"📦 Файлов: {len(info['files'])}\n"
                text += f"💿 Размер: {info['total_size'] / 1024:.2f} KB\n"
                text += f"🗜 Сжато: {info['total_compressed'] / 1024:.2f} KB\n"
                text += f"📊 Сжатие: {info['compression_ratio']}%\n\n"
                if info['metadata']:
                    text += '**📋 Метаданные:**\n'
                    if 'username' in info['metadata']:
                        text += f"👤 @{info['metadata']['username']}\n"
                    if 'first_name' in info['metadata']:
                        text += f"📝 {info['metadata']['first_name']}\n"
                    if 'has_password' in info['metadata']:
                        text += (
                            f"🔐 Пароль: {'Да' if info['metadata']['has_password'] else 'Нет'}\n"
                            )
                    text += '\n'
                text += '**📁 Файлы:**\n'
                for file_info in info['files'][:20]:
                    size_kb = file_info['size'] / 1024
                    text += f"• `{file_info['path']}` ({size_kb:.1f} KB)\n"
                if len(info['files']) > 20:
                    text += f"\n... и еще {len(info['files']) - 20} файлов"
                await msg.edit(text)
            except Exception as e:
                await msg.edit(
                    f'❌ Ошибка анализа архива:\n<code>{str(e)}</code>')
                if os.path.exists(temp_archive):
                    os.remove(temp_archive)

        async def backupinfo_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}backupinfo'):
                return
            try:
                config_files = glob.glob('config*.ini')
                session_files = glob.glob('*.session')
                media_files = glob.glob('info_media_*.*')
                total_size = 0
                for file_path in (config_files + session_files + media_files):
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                text = f'**💾 Информация о данных для backup**\n\n'
                text += f'📄 Конфигов: {len(config_files)}\n'
                text += f'🔑 Сессий: {len(session_files)}\n'
                text += f'🖼 Медиа файлов: {len(media_files)}\n'
                text += (
                    f'💿 Общий размер: {total_size / (1024 * 1024):.2f} MB\n\n')
                text += '**📁 Конфиги:**\n'
                for config_file in config_files[:5]:
                    size = os.path.getsize(config_file) / 1024
                    text += f'• `{config_file}` ({size:.1f} KB)\n'
                if len(config_files) > 5:
                    text += f'• ... и еще {len(config_files) - 5}\n'
                text += f'\n**🔑 Сессии:**\n'
                for session_file in session_files[:5]:
                    size = os.path.getsize(session_file) / 1024
                    text += f'• `{session_file}` ({size:.1f} KB)\n'
                if len(session_files) > 5:
                    text += f'• ... и еще {len(session_files) - 5}\n'
                text += (
                    f'\n💡 Используйте `{self.prefix}backup` для создания резервной копии'
                    )
                await event.edit(text)
            except Exception as e:
                await event.edit(
                    f'❌ Ошибка получения информации:\n<code>{str(e)}</code>')
        client.add_event_handler(backup_handler, events.NewMessage(outgoing
            =True))
        client.add_event_handler(restore_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(backuplist_handler, events.NewMessage(
            outgoing=True))
        client.add_event_handler(backupinfo_handler, events.NewMessage(
            outgoing=True))
