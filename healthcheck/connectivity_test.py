#!/usr/bin/env python3
from selenium import webdriver
import sys
from config_data.config import load_config
from selenium.webdriver.chrome.options import Options

def test_google_connection():
    try:
        # Настройка опций браузера
        options = Options()
        config = load_config()

        # Настройки вебдрайвера
        options._arguments.extend(config.webdriver.options)

        # Настройки Selenoid
        options._caps.update(config.webdriver.capability)

        # Инициализация удаленного браузера
        browser = webdriver.Remote(
            command_executor=config.webdriver.selenoid_url,
            options=options
        )
        
        # Попытка открыть Google
        browser.get("https://www.google.com")
        
        # Проверка заголовка страницы
        title = browser.title.lower()
        browser.quit()
        
        # Проверка успешности подключения
        if "google" in title:
            print("✅ Successfully connected to Google")
            return True
        else:
            print(f"❌ Unexpected title: {title}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_connection()
    sys.exit(0 if success else 1)