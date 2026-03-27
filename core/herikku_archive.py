import os
import json
import zlib
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class HerikkunArchive:
    MAGIC = b'HERIKKU_ARCHIVE_V1'
    SALT = b'herikku_userbot_salt_2026'

    def __init__(self, password=None):
        if password is None:
            password = 'herikku_default_key_do_not_share'
        self.password = password.encode() if isinstance(password, str
            ) else password
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)

    def _derive_key(self):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.
            SALT, iterations=100000, backend=default_backend())
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def create(self, output_path, files_dict, metadata=None):
        try:
            archive_data = {'version': 1, 'created': datetime.now().
                isoformat(), 'metadata': metadata or {}, 'files': {}}
            for archive_path, file_path in files_dict.items():
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    compressed = zlib.compress(file_content, level=9)
                    encoded = base64.b64encode(compressed).decode('utf-8')
                    archive_data['files'][archive_path] = {'content':
                        encoded, 'size': len(file_content),
                        'compressed_size': len(compressed)}
            json_data = json.dumps(archive_data, ensure_ascii=False, indent=2)
            encrypted = self.cipher.encrypt(json_data.encode('utf-8'))
            with open(output_path, 'wb') as f:
                f.write(self.MAGIC)
                f.write(b'\n')
                f.write(encrypted)
            return True
        except Exception as e:
            print(f'Ошибка создания архива: {e}')
            return False

    def extract(self, archive_path, output_dir='.'):
        try:
            with open(archive_path, 'rb') as f:
                magic = f.readline().strip()
                if magic != self.MAGIC:
                    raise ValueError('Неверный формат архива')
                encrypted_data = f.read()
            decrypted = self.cipher.decrypt(encrypted_data)
            archive_data = json.loads(decrypted.decode('utf-8'))
            extracted_files = []
            for archive_file_path, file_info in archive_data['files'].items():
                output_path = os.path.join(output_dir, archive_file_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                compressed = base64.b64decode(file_info['content'])
                file_content = zlib.decompress(compressed)
                with open(output_path, 'wb') as f:
                    f.write(file_content)
                extracted_files.append({'path': output_path, 'size':
                    file_info['size']})
            return {'version': archive_data['version'], 'created':
                archive_data['created'], 'metadata': archive_data[
                'metadata'], 'files': extracted_files}
        except Exception as e:
            print(f'Ошибка извлечения архива: {e}')
            return None

    def list_contents(self, archive_path):
        try:
            with open(archive_path, 'rb') as f:
                magic = f.readline().strip()
                if magic != self.MAGIC:
                    raise ValueError('Неверный формат архива')
                encrypted_data = f.read()
            decrypted = self.cipher.decrypt(encrypted_data)
            archive_data = json.loads(decrypted.decode('utf-8'))
            files_info = []
            total_size = 0
            total_compressed = 0
            for path, info in archive_data['files'].items():
                files_info.append({'path': path, 'size': info['size'],
                    'compressed_size': info['compressed_size']})
                total_size += info['size']
                total_compressed += info['compressed_size']
            return {'version': archive_data['version'], 'created':
                archive_data['created'], 'metadata': archive_data[
                'metadata'], 'files': files_info, 'total_size': total_size,
                'total_compressed': total_compressed, 'compression_ratio': 
                round(100 * (1 - total_compressed / total_size), 2) if 
                total_size > 0 else 0}
        except Exception as e:
            print(f'Ошибка чтения архива: {e}')
            return None
