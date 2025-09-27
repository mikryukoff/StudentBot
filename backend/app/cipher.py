import base64
import os
from dataclasses import dataclass

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


@dataclass
class PassCipher:
    secret_key: str | bytes

    def check_secret_key(self):
        if not self.secret_key:
            raise ValueError(
                "self.secret_key environment variable is not set!"
            )

        # Если ключ - строка, преобразуем в байты, если ключ - байты, оставляем как есть
        if isinstance(self.secret_key, str):
            self.secret_key = self.secret_key.encode('utf-8')

        # Убедимся, что ключ длиной 32 байта (AES-256)
        self.secret_key = self.secret_key.ljust(32, b'0')[:32]

    # Метод для шифрования пароля
    def encrypt_password(self, password: str) -> str:
        self.check_secret_key()

        # Инициализируем режим шифрования
        iv = os.urandom(16)

        cipher = Cipher(
            algorithm=algorithms.AES(self.secret_key),
            mode=modes.CBC(iv),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()

        # Паддинг пароля для AES (блочный шифр)
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_password = (
            padder.update(password.encode('utf-8')) + padder.finalize()
        )

        # Шифруем пароль
        encrypted_password = (
            encryptor.update(padded_password) + encryptor.finalize()
        )

        # Возвращаем зашифрованный пароль в формате base64
        return base64.b64encode(iv + encrypted_password).decode('utf-8')

    # Метод для дешифрования пароля
    def decrypt_password(self, encrypted_password: str) -> str:
        self.check_secret_key()

        # Декодируем зашифрованный пароль из base64
        encrypted_password_bytes = base64.b64decode(encrypted_password)

        # Извлекаем вектор инициализации (IV) из первых 16 байт
        iv = encrypted_password_bytes[:16]
        encrypted_password_bytes = encrypted_password_bytes[16:]

        # Инициализируем расшифровщик
        cipher = Cipher(
            algorithm=algorithms.AES(self.secret_key),
            mode=modes.CBC(iv),
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # Дешифруем пароль
        decrypted_password = (
            decryptor.update(encrypted_password_bytes) + decryptor.finalize()
        )

        # Убираем паддинг
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        original_password = (
            unpadder.update(decrypted_password) + unpadder.finalize()
        )

        return original_password.decode('utf-8')
