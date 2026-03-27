import json
import os
from typing import Dict, Optional


class TextFormatter:
    THEMES_FILE = 'themes.json'
    DEFAULT_THEMES = {'default': {'name': 'По умолчанию', 'emoji': {
        'success': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️',
        'loading': '⏳', 'fire': '🔥', 'star': '⭐', 'rocket': '🚀', 'gear':
        '⚙️', 'package': '📦', 'book': '📚', 'chart': '📊', 'lock': '🔒', 'key':
        '🔑', 'shield': '🛡', 'crown': '👑', 'robot': '🤖', 'lightning': '⚡',
        'heart': '❤️', 'diamond': '💎'}, 'borders': {'top': '═', 'bottom':
        '═', 'left': '║', 'right': '║', 'corner_tl': '╔', 'corner_tr': '╗',
        'corner_bl': '╚', 'corner_br': '╝'}, 'separators': {'line': '─',
        'double': '═', 'dotted': '·', 'wave': '~'}, 'bullets': {'default':
        '•', 'arrow': '→', 'check': '✓', 'cross': '✗', 'star': '★',
        'circle': '○'}}, 'minimal': {'name': 'Минимализм', 'emoji': {
        'success': '✓', 'error': '✗', 'warning': '!', 'info': 'i',
        'loading': '...', 'fire': '*', 'star': '*', 'rocket': '>', 'gear':
        '+', 'package': '#', 'book': '=', 'chart': '|', 'lock': '#', 'key':
        '*', 'shield': '#', 'crown': '*', 'robot': '@', 'lightning': '!',
        'heart': '<3', 'diamond': '*'}, 'borders': {'top': '-', 'bottom':
        '-', 'left': '|', 'right': '|', 'corner_tl': '+', 'corner_tr': '+',
        'corner_bl': '+', 'corner_br': '+'}, 'separators': {'line': '-',
        'double': '=', 'dotted': '.', 'wave': '~'}, 'bullets': {'default':
        '-', 'arrow': '>', 'check': '+', 'cross': 'x', 'star': '*',
        'circle': 'o'}}, 'fancy': {'name': 'Красивый', 'emoji': {'success':
        '✨', 'error': '💥', 'warning': '⚡', 'info': '💡', 'loading': '🔄',
        'fire': '🔥', 'star': '⭐', 'rocket': '🚀', 'gear': '⚙️', 'package':
        '🎁', 'book': '📖', 'chart': '📈', 'lock': '🔐', 'key': '🗝️', 'shield':
        '🛡️', 'crown': '👑', 'robot': '🤖', 'lightning': '⚡', 'heart': '💖',
        'diamond': '💎'}, 'borders': {'top': '━', 'bottom': '━', 'left': '┃',
        'right': '┃', 'corner_tl': '┏', 'corner_tr': '┓', 'corner_bl': '┗',
        'corner_br': '┛'}, 'separators': {'line': '─', 'double': '═',
        'dotted': '┈', 'wave': '〰'}, 'bullets': {'default': '◆', 'arrow':
        '➤', 'check': '✔', 'cross': '✘', 'star': '★', 'circle': '●'}}}

    def __init__(self):
        self.themes = self.DEFAULT_THEMES.copy()
        self.user_themes: Dict[int, str] = {}
        self.load_themes()

    def load_themes(self):
        if os.path.exists(self.THEMES_FILE):
            try:
                with open(self.THEMES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    custom_themes = data.get('custom_themes', {})
                    self.themes.update(custom_themes)
                    self.user_themes = {int(k): v for k, v in data.get(
                        'user_themes', {}).items()}
            except Exception as e:
                print(f'⚠️ Ошибка загрузки тем: {e}')

    def save_themes(self):
        try:
            custom_themes = {k: v for k, v in self.themes.items() if k not in
                self.DEFAULT_THEMES}
            data = {'custom_themes': custom_themes, 'user_themes': {str(k):
                v for k, v in self.user_themes.items()}}
            with open(self.THEMES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f'⚠️ Ошибка сохранения тем: {e}')

    def set_user_theme(self, user_id: int, theme_name: str):
        if theme_name in self.themes:
            self.user_themes[user_id] = theme_name
            self.save_themes()
            return True
        return False

    def get_user_theme(self, user_id: int) ->str:
        return self.user_themes.get(user_id, 'default')

    def get_theme(self, user_id: int) ->Dict:
        theme_name = self.get_user_theme(user_id)
        return self.themes.get(theme_name, self.themes['default'])

    def emoji(self, user_id: int, name: str) ->str:
        theme = self.get_theme(user_id)
        return theme['emoji'].get(name, '•')

    def border(self, user_id: int, name: str) ->str:
        theme = self.get_theme(user_id)
        return theme['borders'].get(name, '─')

    def separator(self, user_id: int, name: str) ->str:
        theme = self.get_theme(user_id)
        return theme['separators'].get(name, '─')

    def bullet(self, user_id: int, name: str) ->str:
        theme = self.get_theme(user_id)
        return theme['bullets'].get(name, '•')

    def box(self, user_id: int, text: str, width: int=40) ->str:
        theme = self.get_theme(user_id)
        lines = text.split('\n')
        result = []
        result.append(theme['borders']['corner_tl'] + theme['borders'][
            'top'] * width + theme['borders']['corner_tr'])
        for line in lines:
            padding = width - len(line)
            result.append(theme['borders']['left'] + line + ' ' * padding +
                theme['borders']['right'])
        result.append(theme['borders']['corner_bl'] + theme['borders'][
            'bottom'] * width + theme['borders']['corner_br'])
        return '\n'.join(result)

    def header(self, user_id: int, text: str, emoji_name: str='star') ->str:
        emoji = self.emoji(user_id, emoji_name)
        sep = self.separator(user_id, 'double')
        return f'{emoji} <b>{text}</b> {emoji}\n{sep * 30}'

    def section(self, user_id: int, title: str, content: str, emoji_name:
        str='info') ->str:
        emoji = self.emoji(user_id, emoji_name)
        sep = self.separator(user_id, 'line')
        return f'{emoji} <b>{title}</b>\n{sep * 20}\n{content}\n'

    def list_item(self, user_id: int, text: str, bullet_name: str='default'
        ) ->str:
        bullet = self.bullet(user_id, bullet_name)
        return f'{bullet} {text}'

    def success(self, user_id: int, text: str) ->str:
        emoji = self.emoji(user_id, 'success')
        return f'{emoji} {text}'

    def error(self, user_id: int, text: str) ->str:
        emoji = self.emoji(user_id, 'error')
        return f'{emoji} {text}'

    def warning(self, user_id: int, text: str) ->str:
        emoji = self.emoji(user_id, 'warning')
        return f'{emoji} {text}'

    def info(self, user_id: int, text: str) ->str:
        emoji = self.emoji(user_id, 'info')
        return f'{emoji} {text}'

    def loading(self, user_id: int, text: str) ->str:
        emoji = self.emoji(user_id, 'loading')
        return f'{emoji} {text}'

    def get_available_themes(self) ->Dict[str, str]:
        return {name: theme['name'] for name, theme in self.themes.items()}


def markdown_to_html(text: str) ->str:
    import re
    text = re.sub('\\*\\*(.+?)\\*\\*', '<b>\\1</b>', text)
    text = re.sub('`([^`]+?)`', '<code>\\1</code>', text)
    text = re.sub('(?<!\\w)_([^_]+?)_(?!\\w)', '<i>\\1</i>', text)
    return text


text_formatter = TextFormatter()
