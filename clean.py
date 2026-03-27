import os
import ast
import astor

def remove_everything_except_code(source_code):
    tree = ast.parse(source_code)
    
    for node in ast.walk(tree):
        # 1. Очищаем docstrings у модулей, классов и функций напрямую
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module)):
            # В новых версиях Python удаление первой строки-константы очищает docstring
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                node.body.pop(0)

        # 2. Удаляем любые "бесхозные" строки в блоках кода (например, внутри if/for)
        if hasattr(node, 'body') and isinstance(node.body, list):
            new_body = []
            for item in node.body:
                # Если это выражение (Expr) и оно является строковой константой — пропускаем
                if isinstance(item, ast.Expr) and isinstance(item.value, (ast.Str, ast.Constant)):
                    continue
                new_body.append(item)
            node.body = new_body

    # astor вернет чистый код без # комментариев и удаленных строк
    return astor.to_source(tree)

def start_cleaning():
    # Скрипт ищет файлы в папке, где он запущен, и глубже
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for root, dirs, files in os.walk(base_path):
        # Пропускаем технические папки, чтобы не сломать окружение
        if any(part in root for part in ['.venv', 'venv', '__pycache__', '.git']):
            continue
            
        for file in files:
            if file.endswith(".py") and file != os.path.basename(__file__):
                full_path = os.path.join(root, file)
                
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Если файл пустой, пропускаем
                    if not content.strip():
                        continue
                        
                    clean_result = remove_everything_except_code(content)
                    
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(clean_result)
                    print(f"✅ Очищен: {full_path}")
                except Exception as e:
                    print(f"❌ Ошибка в {file}: {e}")

if __name__ == "__main__":
    # Напоминание: pip install astor
    start_cleaning()