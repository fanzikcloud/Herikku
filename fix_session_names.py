import os
import glob
from core.text_formatter import TextFormatter


def fix_session_names():
    print(TextFormatter.color('\n🔧 Поиск файлов с опечатками...', 'cyan'))
    typo_files = glob.glob('herriku_account_*.session')
    if not typo_files:
        print(TextFormatter.color('✅ Файлы с опечатками не найдены!', 'green'))
        print(TextFormatter.color(
            'Все файлы сессий имеют правильные имена.\n', 'cyan'))
        return
    print(TextFormatter.color(
        f'📁 Найдено файлов с опечаткой: {len(typo_files)}', 'yellow'))
    print()
    print(TextFormatter.color('Будут переименованы:', 'cyan'))
    for old_file in typo_files:
        new_file = old_file.replace('herriku_', 'herikku_')
        print(TextFormatter.color(f'  {old_file} → {new_file}', 'yellow'))
    print()
    confirm = input(TextFormatter.color(
        'Продолжить переименование? (yes/no): ', 'cyan'))
    if confirm.lower() not in ['yes', 'y', 'да', 'д']:
        print(TextFormatter.color('\n❌ Отменено пользователем\n', 'red'))
        return
    print()
    print(TextFormatter.color('🔄 Переименование файлов...', 'cyan'))
    renamed_count = 0
    error_count = 0
    for old_file in typo_files:
        new_file = old_file.replace('herriku_', 'herikku_')
        try:
            if os.path.exists(new_file):
                print(TextFormatter.color(
                    f'⚠️  Пропущен {old_file}: файл {new_file} уже существует',
                    'yellow'))
                error_count += 1
                continue
            os.rename(old_file, new_file)
            print(TextFormatter.color(f'✅ {old_file} → {new_file}', 'green'))
            renamed_count += 1
            old_journal = f'{old_file}-journal'
            new_journal = f'{new_file}-journal'
            if os.path.exists(old_journal):
                os.rename(old_journal, new_journal)
                print(TextFormatter.color(
                    f'   └─ {old_journal} → {new_journal}', 'green'))
        except Exception as e:
            print(TextFormatter.color(
                f'❌ Ошибка при переименовании {old_file}: {e}', 'red'))
            error_count += 1
    print()
    print(TextFormatter.color('=' * 50, 'cyan'))
    print(TextFormatter.color('📊 Результаты:', 'cyan'))
    print(TextFormatter.color(f'✅ Переименовано: {renamed_count}', 'green'))
    if error_count > 0:
        print(TextFormatter.color(f'❌ Ошибок: {error_count}', 'red'))
    print(TextFormatter.color('=' * 50 + '\n', 'cyan'))
    if renamed_count > 0:
        print(TextFormatter.color(
            '✨ Готово! Теперь все файлы имеют правильные имена.', 'green'))
        print(TextFormatter.color(
            '💡 Можете запустить бота: python main.py\n', 'cyan'))


if __name__ == '__main__':
    try:
        fix_session_names()
    except KeyboardInterrupt:
        print(TextFormatter.color('\n\n❌ Прервано пользователем\n', 'red'))
    except Exception as e:
        print(TextFormatter.color(f'\n❌ Ошибка: {e}\n', 'red'))
        import traceback
        traceback.print_exc()
