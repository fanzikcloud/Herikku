import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.config_manager import load_config
from core.proxy_manager import load_proxy
from core.session_cleaner import check_and_clean_sessions, get_session_files
from core.text_formatter import TextFormatter


async def main():
    print('=' * 60)
    print('🧹 Утилита очистки сессий Herikku Userbot')
    print('=' * 60)
    try:
        config = load_config()
        proxy = load_proxy()
    except Exception as e:
        print(TextFormatter.color(f'❌ Ошибка загрузки конфигурации: {e}',
            'red'))
        return
    api_id = config.getint('Telegram', 'api_id')
    api_hash = config.get('Telegram', 'api_hash')
    device_model = config.get('Telegram', 'device_model')
    system_version = config.get('Telegram', 'system_version')
    session_files = get_session_files(include_bots=True)
    if not session_files:
        print(TextFormatter.color('\nℹ️  Файлы сессий не найдены', 'cyan'))
        print(TextFormatter.color('Нечего проверять!', 'yellow'))
        return
    user_sessions = [f for f in session_files if not f.startswith(
        'inline_bot_session_')]
    bot_sessions = [f for f in session_files if f.startswith(
        'inline_bot_session_')]
    print(TextFormatter.color(
        f'\n📁 Найдено пользовательских сессий: {len(user_sessions)}', 'cyan'))
    if bot_sessions:
        print(TextFormatter.color(
            f'🤖 Найдено bot сессий: {len(bot_sessions)}', 'cyan'))
    print(TextFormatter.color('\nСписок пользовательских сессий:', 'cyan'))
    for i, session_file in enumerate(user_sessions, 1):
        print(TextFormatter.color(f'  {i}. {session_file}', 'yellow'))
    if bot_sessions:
        print(TextFormatter.color('\nСписок bot сессий:', 'cyan'))
        for i, session_file in enumerate(bot_sessions, 1):
            print(TextFormatter.color(f'  {i}. {session_file}', 'yellow'))
    print(TextFormatter.color('\n⚠️  ВНИМАНИЕ!', 'yellow'))
    print(TextFormatter.color(
        'Эта утилита проверит все сессии (включая bot) и удалит неактивные.',
        'yellow'))
    print(TextFormatter.color('Активные сессии будут сохранены.', 'green'))
    try:
        response = input(TextFormatter.color('\nПродолжить? (yes/no): ',
            'cyan'))
        if response.lower() not in ['yes', 'y', 'да', 'д']:
            print(TextFormatter.color('\n❌ Отменено пользователем', 'red'))
            return
    except KeyboardInterrupt:
        print(TextFormatter.color('\n\n❌ Отменено пользователем', 'red'))
        return
    print(TextFormatter.color('\n🔄 Начинаю проверку...', 'cyan'))
    try:
        active_sessions, removed_sessions, active_bots, removed_bots = (await
            check_and_clean_sessions(api_id, api_hash, device_model,
            system_version, proxy, check_bots=True))
        print(TextFormatter.color('\n' + '=' * 60, 'green'))
        print(TextFormatter.color('✅ Очистка завершена успешно!', 'green'))
        print(TextFormatter.color('=' * 60, 'green'))
        total_removed = len(removed_sessions) + len(removed_bots)
        if total_removed > 0:
            print(TextFormatter.color(
                f'\n🗑️  Удалено неактивных сессий: {total_removed}', 'red'))
            if removed_sessions:
                print(TextFormatter.color(
                    f'  • Пользовательских: {len(removed_sessions)}', 'red'))
            if removed_bots:
                print(TextFormatter.color(
                    f'  • Bot сессий: {len(removed_bots)}', 'red'))
            print(TextFormatter.color('Освобождено место на диске!', 'green'))
        else:
            print(TextFormatter.color(
                '\n✨ Все сессии активны! Удалений не требуется.', 'green'))
        total_active = len(active_sessions) + len(active_bots)
        if total_active > 0:
            print(TextFormatter.color(
                f'\n✅ Активных сессий: {total_active}', 'green'))
            if active_sessions:
                print(TextFormatter.color(
                    f'  • Пользовательских: {len(active_sessions)}', 'green'))
            if active_bots:
                print(TextFormatter.color(
                    f'  • Bot сессий: {len(active_bots)}', 'green'))
            print(TextFormatter.color('Эти сессии готовы к использованию.',
                'cyan'))
    except Exception as e:
        print(TextFormatter.color(f'\n❌ Ошибка при проверке: {e}', 'red'))
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(TextFormatter.color('\n\n❌ Прервано пользователем', 'red'))
    except Exception as e:
        print(TextFormatter.color(f'\n❌ Критическая ошибка: {e}', 'red'))
        import traceback
        traceback.print_exc()
