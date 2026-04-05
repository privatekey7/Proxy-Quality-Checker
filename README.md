# 🔍 Proxy Quality Checker

Инструмент для массовой проверки качества HTTP/HTTPS прокси-серверов с использованием PixelScan API. Автоматически проверяет прокси, определяет их качество и сохраняет результаты в отдельные файлы.

**⚠️ Важно:** Инструмент проверяет **HTTP и HTTPS прокси**. SOCKS прокси не поддерживаются.

**GitHub:** [https://github.com/privatekey7/Proxy-Quality-Checker](https://github.com/privatekey7/Proxy-Quality-Checker)

## ✨ Возможности

- ✅ Массовая проверка прокси-серверов
- ✅ Определение качества прокси (high, medium, low)
- ✅ Параллельная обработка (до 50 потоков одновременно)
- ✅ Визуальный прогресс-бар
- ✅ Автоматическая сортировка результатов по качеству
- ✅ Поддержка прокси с авторизацией (user:password)
- ✅ Красивый консольный интерфейс с цветным выводом

## 📋 Требования

- Python 3.7 или выше
- Интернет-соединение

## 🚀 Установка

1. Клонируйте репозиторий или скачайте файлы проекта

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## 📝 Использование

1. Подготовьте файл `proxy.txt` с прокси в формате:
```
ip:port:username:password
192.168.1.1:8080:user1:pass1
192.168.1.2:8080:user2:pass2
```

2. Запустите скрипт:
```bash
python main.py
```

3. Дождитесь завершения проверки. Результаты будут сохранены в папку `results/`:
   - `high_quality_proxies.txt` - прокси высокого качества
   - `medium_quality_proxies.txt` - прокси среднего качества
   - `low_quality_proxies.txt` - прокси низкого качества
   - `not_working_proxies.txt` - нерабочие прокси

## 📊 Формат результатов

После завершения проверки вы увидите статистику:
```
📊 Stats:
   Working: X (high: X, medium: X, low: X)
   Dead: X
   Total: X
```

## ⚙️ Настройки

В файле `main.py` можно изменить следующие параметры:

- `batch_size` (строка 221) - размер батча для обработки (по умолчанию 50)
- `max_workers` (строка 196) - количество параллельных потоков (по умолчанию 50)
- `timeout` (строка 92) - таймаут для проверки прокси в секундах (по умолчанию 15)

## 📁 Структура проекта

```
Proxy_Quality_Checker/
├── main.py              # Основной скрипт
├── proxy.txt            # Файл с прокси для проверки
├── requirements.txt     # Зависимости проекта
├── README.md           # Документация
└── results/            # Папка с результатами (создается автоматически)
    ├── high_quality_proxies.txt
    ├── medium_quality_proxies.txt
    ├── low_quality_proxies.txt
    └── not_working_proxies.txt
```

## 🔧 Зависимости

- `requests` - для HTTP-запросов
- `tqdm` - для отображения прогресс-бара

## 📞 Контакты

Telegram Channel: [https://t.me/privatekey_ai](https://t.me/privatekey_ai)

## ⚠️ Примечания

- **Инструмент проверяет HTTP и HTTPS прокси** (SOCKS не поддерживается)
- Убедитесь, что файл `proxy.txt` существует и содержит валидные HTTP/HTTPS прокси
- Проверка выполняется через PixelScan API
- Таймаут для каждого прокси составляет 15 секунд
- Результаты сохраняются только для прокси, которые были успешно проверены

## 📄 Лицензия

Этот проект предоставляется "как есть" без каких-либо гарантий.

---

# 🔍 Proxy Quality Checker

A tool for bulk checking HTTP/HTTPS proxy server quality using PixelScan API. Automatically checks proxies, determines their quality, and saves results to separate files.

**⚠️ Important:** The tool checks **HTTP and HTTPS proxies**. SOCKS proxies are not supported.

**GitHub:** [https://github.com/privatekey7/Proxy-Quality-Checker](https://github.com/privatekey7/Proxy-Quality-Checker)

## ✨ Features

- ✅ Bulk proxy server checking
- ✅ Proxy quality determination (high, medium, low)
- ✅ Parallel processing (up to 50 threads simultaneously)
- ✅ Visual progress bar
- ✅ Automatic result sorting by quality
- ✅ Support for proxies with authentication (user:password)
- ✅ Beautiful console interface with colored output

## 📋 Requirements

- Python 3.7 or higher
- Internet connection

## 🚀 Installation

1. Clone the repository or download project files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📝 Usage

1. Prepare a `proxy.txt` file with proxies in the format:
```
ip:port:username:password
192.168.1.1:8080:user1:pass1
192.168.1.2:8080:user2:pass2
```

2. Run the script:
```bash
python main.py
```

3. Wait for the check to complete. Results will be saved to the `results/` folder:
   - `high_quality_proxies.txt` - high quality proxies
   - `medium_quality_proxies.txt` - medium quality proxies
   - `low_quality_proxies.txt` - low quality proxies
   - `not_working_proxies.txt` - non-working proxies

## 📊 Result Format

After the check completes, you will see statistics:
```
📊 Stats:
   Working: X (high: X, medium: X, low: X)
   Dead: X
   Total: X
```

## ⚙️ Settings

In the `main.py` file, you can change the following parameters:

- `batch_size` (line 221) - batch size for processing (default: 50)
- `max_workers` (line 196) - number of parallel threads (default: 50)
- `timeout` (line 92) - timeout for proxy check in seconds (default: 15)

## 📁 Project Structure

```
Proxy_Quality_Checker/
├── main.py              # Main script
├── proxy.txt            # File with proxies to check
├── requirements.txt     # Project dependencies
├── README.md           # Documentation
└── results/            # Results folder (created automatically)
    ├── high_quality_proxies.txt
    ├── medium_quality_proxies.txt
    ├── low_quality_proxies.txt
    └── not_working_proxies.txt
```

## 🔧 Dependencies

- `requests` - for HTTP requests
- `tqdm` - for progress bar display

## 📞 Contacts

Telegram Channel: [https://t.me/privatekey_ai](https://t.me/privatekey_ai)

## ⚠️ Notes

- **The tool checks HTTP and HTTPS proxies** (SOCKS is not supported)
- Make sure the `proxy.txt` file exists and contains valid HTTP/HTTPS proxies
- Checking is performed through PixelScan API
- Timeout for each proxy is 15 seconds
- Results are saved only for proxies that were successfully checked

## 📄 License

This project is provided "as is" without any warranties.

