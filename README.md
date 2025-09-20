# 🔮 Таро ТГ бот 

Красивый Telegram‑бот для гадания на картах Таро с реальными изображениями колоды Райдер–Уэйт, поддержкой русского и английского языков, несколькими раскладами и ИИ‑толкованиями. 

> English version: see `README_EN.md`.

## Попробовать

Откройте демо‑бота и протестируйте прямо сейчас:

[![MaterTarotBot](https://img.shields.io/badge/MaterTarotBot-blue?logo=telegram)](https://t.me/MaterTarotBot)

## Возможности

- **Аутентичные карты**: реальные изображения карт Райдер–Уэйт из папки `Cards-jpg/`
- **Мультиязычность**: полностью русская и английская локализации (фразы, названия карт, описания)
- **Несколько раскладов**: Одна карта, Три карты, Кельтский крест, Любовь и отношения
- **ИИ‑толкования**: интерпретации с помощью OpenAI GPT‑4
- **Удобный интерфейс**: инлайн‑кнопки и аккуратное форматирование
- **Готов к продакшну**: Docker/Docker Compose, переменные окружения, логирование

## Быстрый старт (Docker)

### Предварительно
- Установлены Docker и Docker Compose
- Токен Telegram‑бота (от @BotFather)
- Ключ OpenAI API

### 1) Настройте переменные окружения
Создайте/отредактируйте файл `.env`:
```bash
TELEGRAM_BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_openai_api_key
```

### 2) Сборка и запуск

#### Вариант A: Один бот (по умолчанию EN)
```bash
docker-compose --profile single up -d
```

#### Вариант B: Один бот с выбором языка
```bash
# Английский
TAROT_LANGUAGE=en docker-compose --profile single up -d

# Русский
TAROT_LANGUAGE=ru docker-compose --profile single up -d
```

#### Вариант C: Оба языка одновременно
```bash
# Английский бот
docker-compose up -d tarot-bot-en

# Русский бот (дополнительно)
docker-compose --profile russian up -d tarot-bot-ru
```

### 3) Полезные Docker‑команды
```bash
# Сборка образа
docker build -t tarot-bot .

# Запуск образа с языком
docker run -d --name tarot-bot-ru --env-file .env -e TAROT_LANGUAGE=ru tarot-bot
```

## Использование (инлайн)

- Откройте бота в Telegram и нажмите «Начать гадание»
- Выберите расклад из меню
- Введите свой вопрос или выберите «Общее гадание»
- Получите изображения карт и ИИ‑толкование, затем можете начать новое гадание

Доступные расклады:
1. **Одна карта** — быстрый совет на день
2. **Три карты** — прошлое, настоящее, будущее
3. **Кельтский крест** — подробный расклад на 10 карт
4. **Любовь и отношения** — 5 карт о чувствах и паре

## Запуск локально (без Docker)
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск на английском
python main.py -l en

# Запуск на русском
python main.py -l ru
```

Аргументы CLI:
- `-l en` или `--language en` — английский
- `-l ru` или `--language ru` — русский

## Переменные окружения
- `TELEGRAM_BOT_TOKEN` — токен Telegram‑бота
- `OPENAI_API_KEY` — ключ OpenAI API
- `TAROT_LANGUAGE` — язык по умолчанию при запуске в Docker (`en`|`ru`)

## Локализация
- Все строки интерфейса и данные колоды вынесены в `i18n.py`
- Для добавления нового языка: расширьте словари `LANGUAGES`, `TAROT_DECK`, `SPREADS_DATA` и укажите код языка при запуске
- В русской версии учтены склонения мастей (Жезлов/Кубков/Мечей/Пентаклей) и правильные формы «карта/карты/карт»

## Структура проекта
```
TAROT/
├── main.py              # Основное приложение бота
├── i18n.py              # Локализация (строки, колода, расклады)
├── Cards-jpg/           # Изображения карт (78 шт.)
├── requirements.txt     # Python-зависимости
├── Dockerfile           # Конфигурация Docker
├── docker-compose.yml   # Docker Compose
├── .dockerignore        # Игнор для Docker
├── .env                 # Переменные окружения (локально)
├── README.md            # Этот файл (RU)
└── README_EN.md         # README на английском
```

## Технологии
- Python, `python-telegram-bot` 20.x
- OpenAI API (GPT‑4)
- Pillow, aiohttp
- Docker / Docker Compose

## Отладка и наблюдение
```bash
# Логи сервиса
docker-compose logs -f tarot-bot

# Логи конкретного сервиса
docker-compose logs -f tarot-bot-en
docker-compose logs -f tarot-bot-ru

# Остановить все сервисы
docker-compose down
```

## Правовой дисклеймер
Проект создан для образовательных и развлекательных целей. Изображения карт Таро используются в некоммерческих целях.

## Лицензия

MIT — см. файл [LICENSE](LICENSE).
