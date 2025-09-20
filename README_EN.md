# 🔮 Multilingual Tarot Bot

A beautiful Telegram bot that provides tarot card readings using authentic Rider-Waite tarot card images with full support for English and Russian languages.

## Features

- **Authentic Tarot Cards**: Uses real Rider-Waite tarot card images
- **Multilingual Support**: Full English and Russian translations
- **Multiple Spreads**: Single card, Three card, Celtic Cross, and Love spreads
- **AI Interpretations**: Powered by OpenAI GPT-4 for insightful readings
- **Beautiful Interface**: Inline keyboards and rich formatting
- **Docker Support**: Easy deployment with Docker containers

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Telegram Bot Token (from @BotFather)
- OpenAI API Key

### 1. Configure Environment
Edit the `.env` file with your credentials:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Build and Run

#### Option A: Single Bot (English by default)
```bash
docker-compose --profile single up -d
```

#### Option B: Single Bot with Language Selection
```bash
# English bot
TAROT_LANGUAGE=en docker-compose --profile single up -d

# Russian bot
TAROT_LANGUAGE=ru docker-compose --profile single up -d
```

#### Option C: Both Languages Simultaneously
```bash
# Run English bot
docker-compose up -d tarot-bot-en

# Run Russian bot (optional)
docker-compose --profile russian up -d tarot-bot-ru
```

### 3. Manual Docker Commands

#### Build the image:
```bash
docker build -t tarot-bot .
```

#### Run English version:
```bash
docker run -d --name tarot-bot-en --env-file .env -e TAROT_LANGUAGE=en tarot-bot
```

#### Run Russian version:
```bash
docker run -d --name tarot-bot-ru --env-file .env -e TAROT_LANGUAGE=ru tarot-bot
```

## Usage

### Command Line Arguments
- `-l en` or `--language en`: Run in English
- `-l ru` or `--language ru`: Run in Russian

### Using the Bot (Inline)
- Open the bot in Telegram and tap “Get a Reading”.
- Choose a spread from the inline menu.
- Type a question or select “General Reading”.
- Receive cards and an AI interpretation, with buttons to start again or explore spreads.

### Available Spreads
1. **Single Card Reading** - Quick daily guidance
2. **Three Card Spread** - Past, Present, Future
3. **Celtic Cross** - Comprehensive 10-card reading
4. **Love & Relationships** - 5-card spread for romantic matters

## File Structure
```
TAROT/
├── main.py              # Main bot application
├── i18n.py              # Localized strings and deck data
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── .dockerignore        # Docker ignore file
├── Cards-jpg/           # Tarot card images (78 cards)
│   ├── 00-TheFool.jpg
│   ├── 01-TheMagician.jpg
│   └── ...
├── README.md            # Russian README (main)
└── README_EN.md         # This file
```

## Development

### Running Locally (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Run in English
python main.py -l en

# Run in Russian
python main.py -l ru
```

### Logs and Monitoring
```bash
# View logs
docker-compose logs -f tarot-bot

# View specific service logs
docker-compose logs -f tarot-bot-en
docker-compose logs -f tarot-bot-ru
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop tarot-bot-en
```

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**: Check if your Telegram bot token is correct
2. **AI interpretations fail**: Verify your OpenAI API key is valid
3. **Images don't load**: Ensure all tarot card images are in the `Cards-jpg/` directory
4. **Permission denied**: Make sure the bot token has proper permissions

### Debug Commands
```bash
# Check if container is running
docker ps

# Check container logs
docker logs tarot-bot-en

# Enter container for debugging
docker exec -it tarot-bot-en /bin/bash

# Test bot syntax
docker run --rm tarot-bot python -m py_compile main.py
```

## Card Images

The bot includes 78 authentic Rider-Waite tarot card images:
- 22 Major Arcana cards
- 56 Minor Arcana cards (4 suits × 14 cards each)

## Languages Supported

### English
- All interface elements in English
- Card names in traditional English
- Keywords and interpretations in English

### Russian (Русский)
- Полный интерфейс на русском языке
- Названия карт на русском языке
- Ключевые слова и интерпретации на русском языке

## License

This project is for educational and entertainment purposes. Tarot card images are used under fair use for non-commercial purposes.

---

🔮 May the cards guide you on your journey! ✨

