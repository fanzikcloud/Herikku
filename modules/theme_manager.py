from core.base_module import Module
from core.formatting import text_formatter


class ThemeManagerModule(Module):
    NAME = 'Theme Manager'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Управление темами оформления текста'
    DEPENDENCIES = []
    COMMANDS = {'theme': 'Управление темами (.theme help для справки)'}
    CONFIG_ICON = '🎨'

    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        data = event.data.decode('utf-8')
        if data == 'module_theme_manager':
            text = '<b>🎨 Theme Manager</b>\n\n'
            text += '<b>Система управления темами оформления</b>\n\n'
            text += '<b>Основные команды:</b>\n'
            text += '• <code>.theme list</code> - список доступных тем\n'
            text += (
                '• <code>.theme set &lt;название&gt;</code> - установить тему\n'
                )
            text += '• <code>.theme current</code> - текущая тема\n'
            text += (
                '• <code>.theme preview &lt;название&gt;</code> - предпросмотр темы\n\n'
                )
            text += '<b>Доступные темы:</b>\n'
            text += '• <code>default</code> - стандартная тема с эмодзи\n'
            text += '• <code>minimal</code> - минималистичная ASCII тема\n'
            text += (
                '• <code>fancy</code> - красивая тема с Unicode символами\n\n')
            text += '💡 <b>Совет:</b> Темы влияют на оформление всех модулей!'
            buttons = [[Button.inline('◀️ К модулям', b'settings_modules')]]
            await event.edit(text, buttons=buttons)
        else:
            raise Exception('Not our callback')

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def theme_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}theme'):
                return
            me = await self.client.get_me()
            user_id = me.id
            parts = event.text.split()
            if len(parts) == 1 or parts[1] == 'help':
                fmt = text_formatter
                text = fmt.header(user_id, 'Theme Manager - Справка', 'gear')
                text += '\n\n'
                text += fmt.section(user_id, '📋 Основные команды',
                    f"""{fmt.list_item(user_id, f'`{self.prefix}theme list` - показать все доступные темы', 'arrow')}
{fmt.list_item(user_id, f'`{self.prefix}theme current` - показать текущую тему', 'arrow')}
{fmt.list_item(user_id, f'`{self.prefix}theme set <название>` - установить тему', 'arrow')}
{fmt.list_item(user_id, f'`{self.prefix}theme preview <название>` - предпросмотр темы', 'arrow')}"""
                    , 'info')
                text += fmt.section(user_id, '🎨 Доступные темы',
                    f"""{fmt.list_item(user_id, '`default` - стандартная тема с эмодзи ✅❌⚠️', 'star')}
{fmt.list_item(user_id, '`minimal` - минималистичная ASCII тема ✓✗!', 'star')}
{fmt.list_item(user_id, '`fancy` - красивая тема с Unicode ✨💥⚡', 'star')}"""
                    , 'package')
                text += '\n' + fmt.info(user_id,
                    'Темы влияют на оформление всех модулей!')
                text += '\n' + fmt.info(user_id,
                    f'Пример: `{self.prefix}theme set minimal`')
                await event.edit(text)
                return
            command = parts[1]
            if command == 'list':
                fmt = text_formatter
                themes = text_formatter.get_available_themes()
                current_theme = text_formatter.get_user_theme(user_id)
                text = fmt.header(user_id, 'Доступные темы', 'package')
                text += '\n\n'
                for theme_id, theme_name in themes.items():
                    is_current = theme_id == current_theme
                    marker = fmt.emoji(user_id, 'success'
                        ) if is_current else fmt.bullet(user_id, 'circle')
                    text += f'{marker} <b>{theme_id}</b> - {theme_name}'
                    if is_current:
                        text += f" {fmt.emoji(user_id, 'star')} (текущая)"
                    text += '\n'
                text += '\n' + fmt.info(user_id,
                    f'Установить: `{self.prefix}theme set <название>`')
                text += '\n' + fmt.info(user_id,
                    f'Предпросмотр: `{self.prefix}theme preview <название>`')
                await event.edit(text)
            elif command == 'current':
                fmt = text_formatter
                current_theme = text_formatter.get_user_theme(user_id)
                themes = text_formatter.get_available_themes()
                theme_name = themes.get(current_theme, 'Неизвестная')
                text = fmt.header(user_id, 'Текущая тема', 'star')
                text += '\n\n'
                text += (
                    f"{fmt.emoji(user_id, 'info')} <b>ID:</b> `{current_theme}`\n"
                    )
                text += (
                    f"{fmt.emoji(user_id, 'info')} <b>Название:</b> {theme_name}\n\n"
                    )
                text += fmt.section(user_id, 'Примеры оформления',
                    f"""{fmt.success(user_id, 'Успешное сообщение')}
{fmt.error(user_id, 'Сообщение об ошибке')}
{fmt.warning(user_id, 'Предупреждение')}
{fmt.info(user_id, 'Информационное сообщение')}
{fmt.loading(user_id, 'Загрузка...')}"""
                    , 'gear')
                text += fmt.info(user_id,
                    f'Изменить: `{self.prefix}theme set <название>`')
                await event.edit(text)
            elif command == 'set' and len(parts) >= 3:
                theme_name = parts[2]
                themes = text_formatter.get_available_themes()
                if theme_name not in themes:
                    text = text_formatter.error(user_id,
                        f'Тема `{theme_name}` не найдена!')
                    text += '\n\n' + text_formatter.info(user_id,
                        f'Доступные темы: `{self.prefix}theme list`')
                    await event.edit(text)
                    return
                text_formatter.set_user_theme(user_id, theme_name)
                fmt = text_formatter
                text = fmt.header(user_id, 'Тема изменена!', 'success')
                text += '\n\n'
                text += fmt.success(user_id,
                    f'Установлена тема: <b>{themes[theme_name]}</b> (`{theme_name}`)'
                    )
                text += '\n\n'
                text += fmt.section(user_id, 'Примеры новой темы',
                    f"""{fmt.success(user_id, 'Успех')}
{fmt.error(user_id, 'Ошибка')}
{fmt.warning(user_id, 'Предупреждение')}
{fmt.info(user_id, 'Информация')}"""
                    , 'star')
                text += fmt.info(user_id,
                    'Новая тема применена ко всем модулям!')
                await event.edit(text)
            elif command == 'preview' and len(parts) >= 3:
                theme_name = parts[2]
                themes = text_formatter.get_available_themes()
                if theme_name not in themes:
                    text = text_formatter.error(user_id,
                        f'Тема `{theme_name}` не найдена!')
                    text += '\n\n' + text_formatter.info(user_id,
                        f'Доступные темы: `{self.prefix}theme list`')
                    await event.edit(text)
                    return
                old_theme = text_formatter.get_user_theme(user_id)
                text_formatter.user_themes[user_id] = theme_name
                fmt = text_formatter
                text = fmt.header(user_id,
                    f'Предпросмотр: {themes[theme_name]}', 'package')
                text += '\n\n'
                text += fmt.section(user_id, 'Сообщения',
                    f"""{fmt.success(user_id, 'Успешное выполнение операции')}
{fmt.error(user_id, 'Произошла ошибка')}
{fmt.warning(user_id, 'Внимание! Важное предупреждение')}
{fmt.info(user_id, 'Дополнительная информация')}
{fmt.loading(user_id, 'Загрузка данных...')}"""
                    , 'info')
                text += fmt.section(user_id, 'Списки',
                    f"""{fmt.list_item(user_id, 'Обычный элемент списка', 'default')}
{fmt.list_item(user_id, 'Элемент со стрелкой', 'arrow')}
{fmt.list_item(user_id, 'Отмеченный элемент', 'check')}
{fmt.list_item(user_id, 'Отклоненный элемент', 'cross')}
{fmt.list_item(user_id, 'Важный элемент', 'star')}"""
                    , 'book')
                text += fmt.section(user_id, 'Эмодзи',
                    f"""{fmt.emoji(user_id, 'fire')} Fire  {fmt.emoji(user_id, 'star')} Star  {fmt.emoji(user_id, 'rocket')} Rocket  {fmt.emoji(user_id, 'heart')} Heart  {fmt.emoji(user_id, 'diamond')} Diamond
{fmt.emoji(user_id, 'crown')} Crown  {fmt.emoji(user_id, 'shield')} Shield  {fmt.emoji(user_id, 'lock')} Lock  {fmt.emoji(user_id, 'key')} Key  {fmt.emoji(user_id, 'robot')} Robot"""
                    , 'star')
                sep = fmt.separator(user_id, 'line')
                text += f'\n{sep * 30}\n\n'
                text += fmt.info(user_id,
                    f'Установить эту тему: `{self.prefix}theme set {theme_name}`'
                    )
                text_formatter.user_themes[user_id] = old_theme
                await event.edit(text)
            else:
                text = text_formatter.error(user_id,
                    f'Неизвестная команда: `{command}`')
                text += '\n\n' + text_formatter.info(user_id,
                    f'Используйте `{self.prefix}theme help` для справки')
                await event.edit(text)
        client.add_event_handler(theme_handler, events.NewMessage(outgoing=
            True))
