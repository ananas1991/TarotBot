import os
import random
import asyncio
import argparse
from typing import List, Dict, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv
from i18n import LANGUAGES, TAROT_DECK, SPREADS_DATA, SUIT_TRANSLATIONS, RU_SUIT_GENITIVE

# Telegram bot libraries
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    InputMediaPhoto,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode, ChatAction

# OpenAI library
import openai
from openai import AsyncOpenAI

# For image handling
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Tarot Bot with language support')
parser.add_argument('-l', '--language', choices=['en', 'ru'], default='en',
                    help='Language for the bot (en for English, ru for Russian)')
args = parser.parse_args()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGUAGE = args.language

# Card image directory
CARDS_DIR = "/root/TAROT/Cards-jpg"

# Mapping between card names and image filenames
CARD_IMAGE_MAP = {
    # Major Arcana
    "The Fool": "00-TheFool.jpg",
    "The Magician": "01-TheMagician.jpg",
    "The High Priestess": "02-TheHighPriestess.jpg",
    "The Empress": "03-TheEmpress.jpg",
    "The Emperor": "04-TheEmperor.jpg",
    "The Hierophant": "05-TheHierophant.jpg",
    "The Lovers": "06-TheLovers.jpg",
    "The Chariot": "07-TheChariot.jpg",
    "Strength": "08-Strength.jpg",
    "The Hermit": "09-TheHermit.jpg",
    "Wheel of Fortune": "10-WheelOfFortune.jpg",
    "Justice": "11-Justice.jpg",
    "The Hanged Man": "12-TheHangedMan.jpg",
    "Death": "13-Death.jpg",
    "Temperance": "14-Temperance.jpg",
    "The Devil": "15-TheDevil.jpg",
    "The Tower": "16-TheTower.jpg",
    "The Star": "17-TheStar.jpg",
    "The Moon": "18-TheMoon.jpg",
    "The Sun": "19-TheSun.jpg",
    "Judgement": "20-Judgement.jpg",
    "The World": "21-TheWorld.jpg",

    # Minor Arcana - Cups
    "Ace of Cups": "Cups01.jpg",
    "Two of Cups": "Cups02.jpg",
    "Three of Cups": "Cups03.jpg",
    "Four of Cups": "Cups04.jpg",
    "Five of Cups": "Cups05.jpg",
    "Six of Cups": "Cups06.jpg",
    "Seven of Cups": "Cups07.jpg",
    "Eight of Cups": "Cups08.jpg",
    "Nine of Cups": "Cups09.jpg",
    "Ten of Cups": "Cups10.jpg",
    "Page of Cups": "Cups11.jpg",
    "Knight of Cups": "Cups12.jpg",
    "Queen of Cups": "Cups13.jpg",
    "King of Cups": "Cups14.jpg",

    # Minor Arcana - Pentacles
    "Ace of Pentacles": "Pentacles01.jpg",
    "Two of Pentacles": "Pentacles02.jpg",
    "Three of Pentacles": "Pentacles03.jpg",
    "Four of Pentacles": "Pentacles04.jpg",
    "Five of Pentacles": "Pentacles05.jpg",
    "Six of Pentacles": "Pentacles06.jpg",
    "Seven of Pentacles": "Pentacles07.jpg",
    "Eight of Pentacles": "Pentacles08.jpg",
    "Nine of Pentacles": "Pentacles09.jpg",
    "Ten of Pentacles": "Pentacles10.jpg",
    "Page of Pentacles": "Pentacles11.jpg",
    "Knight of Pentacles": "Pentacles12.jpg",
    "Queen of Pentacles": "Pentacles13.jpg",
    "King of Pentacles": "Pentacles14.jpg",

    # Minor Arcana - Swords
    "Ace of Swords": "Swords01.jpg",
    "Two of Swords": "Swords02.jpg",
    "Three of Swords": "Swords03.jpg",
    "Four of Swords": "Swords04.jpg",
    "Five of Swords": "Swords05.jpg",
    "Six of Swords": "Swords06.jpg",
    "Seven of Swords": "Swords07.jpg",
    "Eight of Swords": "Swords08.jpg",
    "Nine of Swords": "Swords09.jpg",
    "Ten of Swords": "Swords10.jpg",
    "Page of Swords": "Swords11.jpg",
    "Knight of Swords": "Swords12.jpg",
    "Queen of Swords": "Swords13.jpg",
    "King of Swords": "Swords14.jpg",

    # Minor Arcana - Wands
    "Ace of Wands": "Wands01.jpg",
    "Two of Wands": "Wands02.jpg",
    "Three of Wands": "Wands03.jpg",
    "Four of Wands": "Wands04.jpg",
    "Five of Wands": "Wands05.jpg",
    "Six of Wands": "Wands06.jpg",
    "Seven of Wands": "Wands07.jpg",
    "Eight of Wands": "Wands08.jpg",
    "Nine of Wands": "Wands09.jpg",
    "Ten of Wands": "Wands10.jpg",
    "Page of Wands": "Wands11.jpg",
    "Knight of Wands": "Wands12.jpg",
    "Queen of Wands": "Wands13.jpg",
    "King of Wands": "Wands14.jpg"
}

"""Language strings moved to i18n.LANGUAGES"""

def t(key: str, **kwargs) -> str:
    """Get translated text for the current language"""
    text = LANGUAGES.get(LANGUAGE, LANGUAGES['en']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

"""TAROT_DECK moved to i18n.TAROT_DECK"""

"""SPREADS_DATA moved to i18n.SPREADS_DATA"""

"""SUIT_TRANSLATIONS and RU_SUIT_GENITIVE moved to i18n"""

def get_spread_info(spread_id: str) -> dict:
    """Get localized spread information"""
    spread_data = SPREADS_DATA[spread_id]
    return {
        "name": spread_data["name"][LANGUAGE],
        "description": spread_data["description"][LANGUAGE],
        "positions": spread_data["positions"][LANGUAGE]
    }

def get_card_name(card_data: dict) -> str:
    """Get localized card name"""
    if "name" in card_data and isinstance(card_data["name"], dict):
        return card_data["name"][LANGUAGE]
    return card_data.get("name", "Unknown Card")

def get_card_keywords(card_data: dict) -> str:
    """Get localized card keywords"""
    if "keywords" in card_data and isinstance(card_data["keywords"], dict):
        return card_data["keywords"][LANGUAGE]
    return card_data.get("keywords", t("mystery_awaits"))

class TarotBot:
    def __init__(self):
        self.user_sessions = {}

    async def generate_card_image(self, card_name: str, position: str = None) -> BytesIO:
        """Load and return real tarot card image"""
        try:
            # Get the filename for this card
            filename = CARD_IMAGE_MAP.get(card_name)

            if filename:
                # Load the real card image
                image_path = os.path.join(CARDS_DIR, filename)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        img_bytes = BytesIO(img_file.read())
                        img_bytes.seek(0)
                        return img_bytes
                else:
                    logger.warning(f"Image file not found: {image_path}")
            else:
                logger.warning(f"No image mapping found for card: {card_name}")

            # Fallback: create a simple card with text if image not found
            return await self.create_fallback_image(card_name, position)

        except Exception as e:
            logger.error(f"Error loading card image for {card_name}: {e}")
            return await self.create_fallback_image(card_name, position)

    async def create_fallback_image(self, card_name: str, position: str = None) -> BytesIO:
        """Create a simple fallback image when real card image is not available"""
        width, height = 400, 600
        img = Image.new('RGB', (width, height), color='#2c1810')
        draw = ImageDraw.Draw(img)

        # Add border
        border_color = '#ffd700'
        draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)

        # Try to use a nice font, fallback to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 24)
            position_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            position_font = ImageFont.load_default()

        # Add card name (wrapped if too long)
        words = card_name.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            text_bbox = draw.textbbox((0, 0), test_line, font=title_font)
            text_width = text_bbox[2] - text_bbox[0]

            if text_width <= width - 40:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        # Draw the text lines
        y_offset = height // 2 - (len(lines) * 30) // 2
        for line in lines:
            text_bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, y_offset), line, fill='#ffffff', font=title_font)
            y_offset += 35

        # Add position if specified
        if position:
            pos_bbox = draw.textbbox((0, 0), position, font=position_font)
            pos_width = pos_bbox[2] - pos_bbox[0]
            pos_x = (width - pos_width) // 2
            draw.text((pos_x, height - 60), position, fill=border_color, font=position_font)

        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

    async def get_ai_interpretation(self, cards: List[Dict], spread_type: str, question: str = None) -> str:
        """Get AI interpretation of the cards"""
        
        # Build the prompt
        spread_info = get_spread_info(spread_type)
        cards_description = "\n".join([
            f"{i+1}. {spread_info['positions'][i]}: {get_card_name(card) if 'english_name' not in card else card['name']} - {get_card_keywords(card) if 'english_name' not in card else card.get('keywords', '')}"
            for i, card in enumerate(cards)
        ])

        language_instruction = "Please respond in Russian." if LANGUAGE == 'ru' else "Please respond in English."

        prompt = f"""You are a wise and mystical tarot reader. Provide an insightful interpretation of this {spread_info['name']} tarot reading. {language_instruction}

The cards drawn are:
{cards_description}

{"The querent asks: " + question if question else "No specific question was asked."}

Provide a meaningful, personalized interpretation that:
1. Explains what each card means in its position
2. Describes how the cards relate to each other
3. Offers practical guidance and insights
4. Maintains a mystical but helpful tone
5. Is encouraging and empowering

Keep the response concise but meaningful (around 200-300 words)."""

        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a wise, empathetic tarot reader who provides insightful and meaningful interpretations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return t('mystic_energies_clouded')

    def draw_cards(self, num_cards: int) -> List[Dict]:
        """Draw random cards from the deck"""
        all_cards = []

        # Add major arcana
        all_cards.extend(TAROT_DECK["major_arcana"])

        # Add minor arcana
        for suit, cards_data in TAROT_DECK["minor_arcana"].items():
            cards_list = cards_data[LANGUAGE]
            suit_name = SUIT_TRANSLATIONS[LANGUAGE][suit]

            for i, card in enumerate(cards_list):
                # Create the English name for image mapping
                english_card = cards_data["en"][i]
                english_suit = SUIT_TRANSLATIONS["en"][suit]
                english_name = f"{english_card} of {english_suit}"

                # Create the localized name
                if LANGUAGE == "ru":
                    suit_case = RU_SUIT_GENITIVE[suit]
                    localized_name = f"{card} {suit_case}"
                else:
                    localized_name = f"{card} of {suit_name}"

                all_cards.append({
                    "name": localized_name,
                    "english_name": english_name,  # Keep for image mapping
                    "keywords": self.get_minor_arcana_keywords(english_card, suit)
                })

        # Draw random cards without replacement
        drawn_cards = random.sample(all_cards, min(num_cards, len(all_cards)))
        return drawn_cards

    def get_minor_arcana_keywords(self, card: str, suit: str) -> str:
        """Get keywords for minor arcana cards"""
        suit_themes = {
            "en": {
                "wands": "creativity, action, inspiration",
                "cups": "emotions, relationships, intuition",
                "swords": "thoughts, communication, conflict",
                "pentacles": "material, career, manifestation"
            },
            "ru": {
                "wands": "творчество, действие, вдохновение",
                "cups": "эмоции, отношения, интуиция",
                "swords": "мысли, общение, конфликт",
                "pentacles": "материальное, карьера, проявление"
            }
        }

        theme = suit_themes[LANGUAGE][suit]

        if card == "Ace":
            if LANGUAGE == "ru":
                return f"новые начинания в сфере: {theme}"
            else:
                return f"new beginnings in {theme}"
        elif card in ["Page", "Knight", "Queen", "King"]:
            if LANGUAGE == "ru":
                return f"личностный аспект, {theme}"
            else:
                return f"personality aspect, {theme}"
        else:
            return theme

# Russian pluralization helper for card count labels
def plural_ru(n: int, one: str, few: str, many: str) -> str:
    """Russian pluralization: 1 карта, 2-4 карты, 5-0 карт (except teens)."""
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return few
    return many

# Handler functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message and show inline menu."""
    welcome_message = f"""{t('welcome_title')}

{t('welcome_message')}

{t('use_buttons')}

{t('cards_reveal')}"""

    keyboard = [
        [InlineKeyboardButton(t('btn_get_reading'), callback_data="new_reading")],
        [InlineKeyboardButton(t('btn_learn_spreads'), callback_data="show_spreads")],
        [InlineKeyboardButton(t('btn_help'), callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a new reading"""
    keyboard = []
    for spread_id in SPREADS_DATA.keys():
        spread_info = get_spread_info(spread_id)
        count = len(spread_info['positions'])
        if LANGUAGE == 'ru':
            word = plural_ru(count, 'карта', 'карты', 'карт')
        else:
            word = 'card' if count == 1 else 'cards'
        keyboard.append([InlineKeyboardButton(
            f"{spread_info['name']} ({count} {word})",
            callback_data=f"spread_{spread_id}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = f"""{t('choose_spread')}

{t('select_reading')}"""

    if update.message:
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    bot = TarotBot()
    
    if query.data == "new_reading":
        await reading(update, context)
    
    elif query.data == "show_spreads":
        message = f"{t('available_spreads')}\n\n"
        for spread_id in SPREADS_DATA.keys():
            spread_info = get_spread_info(spread_id)
            message += f"*{spread_info['name']}*\n"
            message += f"_{spread_info['description']}_\n"
            message += f"{t('cards').capitalize()}: {len(spread_info['positions'])}\n\n"

        keyboard = [[InlineKeyboardButton(t('btn_start_reading'), callback_data="new_reading")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    elif query.data.startswith("spread_"):
        spread_type = query.data.replace("spread_", "")
        spread_info = get_spread_info(spread_type)

        # Store the spread type for this user
        user_id = query.from_user.id
        context.user_data['spread_type'] = spread_type

        message = f"""{t('spread_selected', spread_name=spread_info['name'])}

_{spread_info['description']}_

{t('ask_question')}

{t('type_question')}"""

        keyboard = [[InlineKeyboardButton(t('btn_general_reading'), callback_data="general_reading")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

        # Set state to expect question
        context.user_data['expecting_question'] = True
    
    elif query.data == "general_reading":
        await perform_reading(update, context, question=None)
    
    elif query.data == "help":
        help_text = f"""{t('help_guide')}

{t('how_to_use')}
{t('help_step1')}
{t('help_step2')}
{t('help_step3')}
{t('help_step4')}

{t('spread_types')}
{t('single_card_desc')}
{t('three_card_desc')}
{t('celtic_cross_desc')}
{t('love_spread_desc')}

{t('tips_better')}
{t('tip1')}
{t('tip2')}
{t('tip3')}
{t('tip4')}

{t('tarot_reminder')}"""

        await query.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's question for the reading"""
    if context.user_data.get('expecting_question'):
        question = update.message.text
        context.user_data['expecting_question'] = False
        await perform_reading(update, context, question=question)

async def perform_reading(update: Update, context: ContextTypes.DEFAULT_TYPE, question: str = None):
    """Perform the actual tarot reading"""
    # Send typing action
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id
    
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    # Get spread type
    spread_type = context.user_data.get('spread_type', 'three_card')
    spread_info = get_spread_info(spread_type)
    
    # Draw cards
    bot = TarotBot()
    cards = bot.draw_cards(len(spread_info['positions']))
    
    # Store reading in history
    user_id = update.effective_user.id
    if 'history' not in context.user_data:
        context.user_data['history'] = []
    
    context.user_data['history'].append({
        'date': datetime.now().isoformat(),
        'spread': spread_type,
        'cards': cards,
        'question': question
    })
    
    # Send initial message
    intro_message = f"""{t('your_reading', spread_name=spread_info['name'])}

{t('your_question', question=question) if question else t('general_reading_msg')}

{t('drawing_cards')}"""
    
    message = await context.bot.send_message(
        chat_id=chat_id,
        text=intro_message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Send each card with image
    media_group = []
    for i, card in enumerate(cards):
        position = spread_info['positions'][i]

        # Use english_name for image mapping if it exists (minor arcana), otherwise use the card name
        image_name = card.get('english_name', get_card_name(card))
        card_image = await bot.generate_card_image(image_name, position)

        # Get localized card name and keywords
        if 'english_name' in card:  # Minor arcana
            card_name = card['name']
            keywords = card.get('keywords', t('mystery_awaits'))
        else:  # Major arcana
            card_name = get_card_name(card)
            keywords = get_card_keywords(card)

        # Send individual card message
        card_text = f"""🎴 {t('position', position=i+1, position_name=position)}
{t('card', card_name=card_name)}
{t('keywords', keywords=keywords)}"""
        
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=card_image,
            caption=card_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Small delay between cards for dramatic effect
        await asyncio.sleep(1)
    
    # Get AI interpretation
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    interpretation = await bot.get_ai_interpretation(cards, spread_type, question)
    
    # Send interpretation
    final_message = f"""{t('divine_interpretation')}

{interpretation}

{t('remember_destiny')}

{t('another_reading')}"""

    keyboard = [
        [InlineKeyboardButton(t('btn_new_reading'), callback_data="new_reading")],
        [InlineKeyboardButton(t('btn_learn_spreads'), callback_data="show_spreads")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=final_message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's reading history"""
    user_history = context.user_data.get('history', [])

    if not user_history:
        await update.message.reply_text(t('no_readings'))
        return

    message = f"{t('recent_readings')}\n\n"
    for reading in user_history[-5:]:  # Show last 5 readings
        date = datetime.fromisoformat(reading['date']).strftime("%B %d, %Y at %I:%M %p")
        spread_name = get_spread_info(reading['spread'])['name']
        message += f"*{date}*\n"
        message += f"{t('spread', spread_name=spread_name)}\n"
        if reading.get('question'):
            message += f"{t('question', question=reading['question'])}\n"
        message += "\n"

    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message focusing on inline controls."""
    help_text = f"""{t('help_guide')}

{t('how_to_use')}
{t('help_step1')}
{t('help_step2')}
{t('help_step3')}
{t('help_step4')}

{t('tips_better')}
{t('tip1')}
{t('tip2')}
{t('tip3')}
{t('tip4')}

{t('guide_you')}"""

    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def setup_bot_commands(application):
    """Clear bot command menu to encourage inline usage."""
    await application.bot.set_my_commands([])

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reading", reading))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("spreads", lambda u, c: button_callback(u, c)))

    # Button handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Message handler for questions
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    # Set up bot commands on startup
    application.post_init = setup_bot_commands

    # Run the bot
    print(t('bot_starting'))
    application.run_polling()

if __name__ == '__main__':
    main()
