from telebot import TeleBot, types
import helpers.config as config 
from database import Database as DB
import os, telebot, requests
from telebot.types import *
from telebot import custom_filters
import helpers.config as config 
import helpers.utility as utility 
import helpers.buttons as buttons
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

db = DB()

bot = TeleBot(config.BOT_TOKEN, parse_mode="HTML")

DBOOKS_API_BASE = 'https://www.dbooks.org/api'
DBOOKS_SEARCH_URL = f'{DBOOKS_API_BASE}/search'
DBOOKS_BOOK_URL = f'{DBOOKS_API_BASE}/book'

BOOK_TEXT_TEMPLATE = '''📚 {title}
{subtitle_line}
👨‍🏫 {authors}
'''

BOOK_TEXT_TEMPLATE_I = '''{title}
{subtitle_line}
Authors: {authors}
'''

users = {}

def search_books_dbooks(query):
    """Search for books using dBooks.org API"""
    logger.info(f"Searching for book: {query}")
    try:
        url = f"{DBOOKS_SEARCH_URL}/{query}"
        logger.info(f"Requesting URL: {url}")
        
        response = requests.get(url, timeout=10)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                books = data.get('books', [])
                logger.info(f"Found {len(books)} books")
                return books[:10]  # Limit to 10 books
            else:
                logger.warning(f"API returned status: {data.get('status')}")
                return []
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error searching books: {e}")
        return []

def get_book_details(book_id):
    """Get detailed book information including download URL"""
    logger.info(f"Getting details for book ID: {book_id}")
    try:
        url = f"{DBOOKS_BOOK_URL}/{book_id}"
        logger.info(f"Requesting URL: {url}")
        
        response = requests.get(url, timeout=10)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                logger.info("Book details retrieved successfully")
                return data
            else:
                logger.warning(f"API returned status: {data.get('status')}")
                return None
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting book details: {e}")
        return None

def send_file(callback):
    """Send download link to user"""
    query = callback
    book_id = query.data.split('_')[1]
    
    # Handle both inline and regular callbacks
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    
    bot.send_message(chat_id, "🔍 Getting download link...")
    
    book_details = get_book_details(book_id)
    
    if book_details and book_details.get('download'):
        download_url = book_details['download']
        title = book_details.get('title', 'Unknown')
        
        message = f"📚 <b>{title}</b>\n\n"
        message += f"📎 <a href='{download_url}'>Click here to download</a>\n\n"
        message += "<i>The download will start in your browser.</i>"
        
        bot.send_message(chat_id, message, disable_web_page_preview=False)
        
        try:
            db.inc_total_books(callback.from_user.id)
        except:
            pass
    else:
        bot.send_message(chat_id, "❌ Unable to get download link. Please try again later.")
    
    return 1

def search_book(name):
    """Wrapper function for backward compatibility"""
    return search_books_dbooks(name)
    
@bot.inline_handler(lambda query: True)
def handle_inline_query(query):
    books = search_book(str(query.query))
    try:        
        results = []
        for idx, book in enumerate(books):
            button_data = f'link_{book["id"]}'
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("⬇️ Download", callback_data=button_data))
            text = "Search result:\n\n"
            subtitle_line = f"\n{book.get('subtitle')}\n" if book.get('subtitle') else ""
            book_data = {
                'title': book.get('title', 'Unknown'),
                'authors': book.get('authors', 'Unknown'),
                'subtitle_line': subtitle_line
            }
            text += BOOK_TEXT_TEMPLATE_I.format(**book_data)
            results.append(
               InlineQueryResultArticle(
                id=idx,
                title=book.get('title', 'Unknown'),
                thumbnail_url=book.get('image', ''),
                reply_markup=keyboard,
                description=f"Authors: {book.get('authors', 'Unknown')}",
                input_message_content=types.InputTextMessageContent(message_text=text),
         )
        )        
        bot.answer_inline_query(query.id, results)

    except Exception as e:
        logger.error(f"Error in inline query: {e}")
        pass
    
def search_book_handler(message):
    msg = bot.reply_to(message, "<i>Looking for this book...🔍</i>")
    text = message.text
    books = search_book(text)    
    if not books:
        bot.edit_message_text("❌ No books found for your search.", chat_id=message.chat.id, message_id=msg.message_id)
        return 1    
    bot.set_state(message.from_user.id, "search", message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    	data["result"] = books
    
    markup = InlineKeyboardMarkup()
    book = books[0]
    subtitle_line = f"\n{book.get('subtitle')}\n" if book.get('subtitle') else ""
    book_data = {
        'title': book.get('title', 'Unknown'),
        'authors': book.get('authors', 'Unknown'),
        'subtitle_line': subtitle_line
    }
    response_text = BOOK_TEXT_TEMPLATE.format(**book_data)

    button_data = f'link_{book["id"]}'   
    markup.add(InlineKeyboardButton("⬇️", callback_data=button_data), InlineKeyboardButton("⏩", callback_data="page_2"))
    markup.add(InlineKeyboardButton("❌", callback_data="cancel"))
    bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"<b>{len(books)} books found for this search🔍</b>")    
    
    # Send with photo if available
    if book.get('image'):
        bot.send_photo(message.chat.id, book['image'], caption=response_text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, response_text, reply_markup=markup)
    return 1

@bot.message_handler(commands=["start"])
def start(message):
	user = db.find_user(user_id=int(message.from_user.id))
	if user:
		accepted = db.check_accept(int(message.from_user.id))
		if accepted:
			bot.send_message(message.chat.id, utility.WELCOME_MSG.format(message.from_user.first_name, bot.get_me().first_name, bot.get_me().username), reply_markup=buttons.welcome_btns())
		else:
			return bot.send_message(message.chat.id, utility.DISCLAIMER_MSG, reply_markup=buttons.tos_btn())	
	else:
		db.save_user(user_id=message.from_user.id)
		return bot.send_message(message.chat.id, utility.DISCLAIMER_MSG, reply_markup=buttons.tos_btn())		

@bot.message_handler(commands=["stats"])
def getStats(message):
	is_admin = db.is_admin(message.from_user.id)
	if is_admin:
		bot.send_message(message.chat.id, f"Total users: {db.get_stats()}")
	else:
		return None

@bot.message_handler(commands=["tos"])
def show_tos(message):
	bot.send_message(message.chat.id, utility.DISCLAIMER_MSG, reply_markup=buttons.back_btn())

@bot.message_handler(commands=["help"])
def show_help(message):
	bot.send_message(message.chat.id, utility.HELP_MSG.format(bot.get_me().username, bot.get_me().username), reply_markup=buttons.back_btn())

@bot.message_handler(func=lambda message: True)
def handle_message(message):
	if "Search result:" in message.text:
		return 
	user_id = message.from_user.id
	accepted = db.check_accept(int(message.from_user.id))
	if accepted:		
		search_book_handler(message)
	else:
		return bot.send_message(message.chat.id, utility.DISCLAIMER_MSG, reply_markup=buttons.tos_btn())	

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("page"), state="search")
def pagination(callback):    
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        books = data["result"]
        page = int(callback.data.split("_")[1])
        start = (page - 1) * 1
        end = start + 1
        items = books[start:end]
        buttons = []
        markup = InlineKeyboardMarkup()
        for i, book in enumerate(items):
            subtitle_line = f"\n{book.get('subtitle')}\n" if book.get('subtitle') else ""
            book_data = {
                'title': book.get('title', 'Unknown'),
                'authors': book.get('authors', 'Unknown'),
                'subtitle_line': subtitle_line
            }
            response_text = BOOK_TEXT_TEMPLATE.format(**book_data)
            button_data = f'link_{book["id"]}'
            if page > 1:
                buttons.append(InlineKeyboardButton("⏪", callback_data=f"page_{page - 1}"))
            if len(books) > end:
                buttons.append(InlineKeyboardButton("⏩", callback_data=f"page_{page + 1}"))
            buttons.append(InlineKeyboardButton("⬇️", callback_data=button_data))
            buttons.append(InlineKeyboardButton("❌", callback_data="cancel"))
            markup.add(*buttons)
            
            # Send with photo if available
            if book.get('image'):
                try:
                    bot.edit_message_media(
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        media=types.InputMediaPhoto(book['image'], caption=response_text),
                        reply_markup=markup
                    )
                except:
                    # Fallback if message doesn't have photo
                    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=response_text, reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=response_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("page"))
def no_state_page(callback):
    state = bot.get_state(callback.message.chat.id, callback.from_user.id)
    if not state:
    	bot.delete_message(callback.message.chat.id, callback.message.message_id)
    	return bot.send_message(callback.message.chat.id, "<i>Request timeout\nTry Again:)</i>")
    else:
    	pass

@bot.callback_query_handler(func = lambda callback: callback.data.startswith("link_"))
def ans_l(callback):
	send_file(callback)
	

@bot.callback_query_handler(func = lambda callback: callback.data.startswith("cancel"))
def ans_c(callback):
	bot.answer_callback_query(callback.id, "Cancelled")
	state = bot.get_state(callback.from_user.id, callback.message.chat.id)
	if state:
		bot.delete_state(callback.from_user.id, callback.message.chat.id)
		bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
	else:
		bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

@bot.callback_query_handler(func = lambda callback: True)
def ans(callback):
	if callback.data == "continue":
		db.accepted_tos(callback.from_user.id)
		return bot.edit_message_text(utility.WELCOME_MSG.format(callback.from_user.first_name, bot.get_me().first_name, bot.get_me().username), chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=buttons.welcome_btns())
	if callback.data == "help":
		bot.edit_message_text(utility.HELP_MSG.format(bot.get_me().username, bot.get_me().username), chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=buttons.back_btn())	
	if callback.data == "back":
		bot.edit_message_text(utility.WELCOME_MSG.format(callback.from_user.first_name, bot.get_me().first_name, bot.get_me().username), chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=buttons.welcome_btns())	
		
bot.add_custom_filter(custom_filters.StateFilter(bot))
