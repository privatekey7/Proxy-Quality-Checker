import subprocess
import sys
import os
import venv
import platform
import requests
import zipfile
import tarfile
import shutil

def install_base_requirements():
    """Установка базовых требований"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "colorama", "requests"], check=True)
        # После установки можно импортировать
        from colorama import init, Fore, Style
        init()
        return init, Fore, Style
    except Exception as e:
        print(f"Ошибка при установке базовых требований: {e}")
        sys.exit(1)

# Получаем colorama после установки
init, Fore, Style = install_base_requirements()

def check_firefox():
    """Проверка установлен ли Firefox"""
    firefox_download_url = "https://www.mozilla.org/firefox/download/thanks/"
    
    if sys.platform == "win32":
        firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        if not os.path.exists(firefox_path):
            firefox_path = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        if not os.path.exists(firefox_path):
            print(f"{Fore.RED}Firefox не установлен!{Style.RESET_ALL}")
            print(f"Пожалуйста, скачайте Firefox: {Fore.CYAN}{firefox_download_url}{Style.RESET_ALL}")
            return False
    else:
        try:
            subprocess.run(['firefox', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            print(f"{Fore.RED}Firefox не установлен!{Style.RESET_ALL}")
            print(f"Пожалуйста, скачайте Firefox: {Fore.CYAN}{firefox_download_url}{Style.RESET_ALL}")
            return False
    return True

def install_geckodriver():
    """Установка geckodriver"""
    print("Установка geckodriver...")
    
    # Определяем систему и архитектуру
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # URL для последней версии geckodriver
    if system == "windows":
        url = "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-win64.zip"
        filename = "geckodriver.zip"
    else:
        url = "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz"
        filename = "geckodriver.tar.gz"
    
    # Создаем папку drivers если её нет
    if not os.path.exists('drivers'):
        os.makedirs('drivers')
    
    # Скачиваем geckodriver
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    # Распаковываем
    if system == "windows":
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall('drivers')
    else:
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall('drivers')
    
    # Удаляем архив
    os.remove(filename)
    
    # Добавляем путь к драйверу в переменную окружения PATH
    driver_path = os.path.abspath('drivers')
    os.environ["PATH"] = f"{driver_path};{os.environ['PATH']}"
    
    print(f"Geckodriver успешно установлен в {driver_path}")

def setup_virtual_environment():
    # Проверяем наличие Firefox
    if not check_firefox():
        sys.exit(1)
    
    # Создаем директорию для виртуального окружения
    venv_dir = "venv"
    
    print("Создание виртуального окружения...")
    venv.create(venv_dir, with_pip=True)
    
    # Определяем путь к pip
    if sys.platform == "win32":
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # Устанавливаем зависимости
    print("Установка зависимостей...")
    requirements = [
        "selenium",
        "requests",
        "colorama",
        "tqdm"
    ]
    
    for package in requirements:
        subprocess.run([pip_path, "install", package])
    
    # Устанавливаем geckodriver
    install_geckodriver()
    
    print("\nУстановка завершена!")
    print("\nДля активации окружения используйте:")
    if sys.platform == "win32":
        print(f"    {venv_dir}\\Scripts\\activate")
    else:
        print(f"    source {venv_dir}/bin/activate")

if __name__ == "__main__":
    setup_virtual_environment() 