import json
import os
from typing import Set, Dict, Optional


class PermissionManager:
    PERMISSIONS_FILE = 'permissions.json'

    def __init__(self):
        self.permissions: Dict[int, Dict] = {}
        self.main_account_id: Optional[int] = None
        self.load_permissions()

    def load_permissions(self):
        if os.path.exists(self.PERMISSIONS_FILE):
            try:
                with open(self.PERMISSIONS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.permissions = {int(k): v for k, v in data.get(
                        'accounts', {}).items()}
                    self.main_account_id = data.get('main_account_id')
            except Exception as e:
                print(f'⚠️ Ошибка загрузки прав: {e}')

    def save_permissions(self):
        try:
            data = {'main_account_id': self.main_account_id, 'accounts': {
                str(k): v for k, v in self.permissions.items()}}
            with open(self.PERMISSIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f'⚠️ Ошибка сохранения прав: {e}')

    def set_main_account(self, user_id: int):
        self.main_account_id = user_id
        if user_id not in self.permissions:
            self.permissions[user_id] = {'role': 'owner',
                'disabled_commands': [], 'disabled_modules': [],
                'custom_settings': {}}
        else:
            self.permissions[user_id]['role'] = 'owner'
        self.save_permissions()

    def is_main_account(self, user_id: int) ->bool:
        return user_id == self.main_account_id

    def add_account(self, user_id: int, role: str='user'):
        if user_id not in self.permissions:
            self.permissions[user_id] = {'role': role, 'disabled_commands':
                [], 'disabled_modules': [], 'custom_settings': {}}
            self.save_permissions()

    def disable_command(self, user_id: int, command: str):
        if user_id in self.permissions:
            if command not in self.permissions[user_id]['disabled_commands']:
                self.permissions[user_id]['disabled_commands'].append(command)
                self.save_permissions()

    def enable_command(self, user_id: int, command: str):
        if user_id in self.permissions:
            if command in self.permissions[user_id]['disabled_commands']:
                self.permissions[user_id]['disabled_commands'].remove(command)
                self.save_permissions()

    def disable_module(self, user_id: int, module: str):
        if user_id in self.permissions:
            if module not in self.permissions[user_id]['disabled_modules']:
                self.permissions[user_id]['disabled_modules'].append(module)
                self.save_permissions()

    def enable_module(self, user_id: int, module: str):
        if user_id in self.permissions:
            if module in self.permissions[user_id]['disabled_modules']:
                self.permissions[user_id]['disabled_modules'].remove(module)
                self.save_permissions()

    def can_use_command(self, user_id: int, command: str) ->bool:
        if self.is_main_account(user_id):
            return True
        if user_id not in self.permissions:
            return True
        return command not in self.permissions[user_id]['disabled_commands']

    def can_use_module(self, user_id: int, module: str) ->bool:
        if self.is_main_account(user_id):
            return True
        if user_id not in self.permissions:
            return True
        return module not in self.permissions[user_id]['disabled_modules']

    def get_disabled_commands(self, user_id: int) ->list:
        if user_id in self.permissions:
            return self.permissions[user_id]['disabled_commands']
        return []

    def get_disabled_modules(self, user_id: int) ->list:
        if user_id in self.permissions:
            return self.permissions[user_id]['disabled_modules']
        return []

    def get_role(self, user_id: int) ->str:
        if self.is_main_account(user_id):
            return 'owner'
        if user_id in self.permissions:
            return self.permissions[user_id].get('role', 'user')
        return 'user'

    def set_custom_setting(self, user_id: int, key: str, value):
        if user_id not in self.permissions:
            self.add_account(user_id)
        self.permissions[user_id]['custom_settings'][key] = value
        self.save_permissions()

    def get_custom_setting(self, user_id: int, key: str, default=None):
        if user_id in self.permissions:
            return self.permissions[user_id]['custom_settings'].get(key,
                default)
        return default

    def get_all_accounts(self) ->Dict[int, Dict]:
        return self.permissions


permission_manager = PermissionManager()
