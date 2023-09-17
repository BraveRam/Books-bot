from telebot import TeleBot, types
import helpers.config as config 
from database import Database as DB
from bs4 import BeautifulSoup
import os, telebot, requests
from telebot.types import *
from telebot import custom_filters
import helpers.config as config 
import helpers.utility as utility 
import helpers.buttons as buttons

bot = TeleBot(config.BOT_TOKEN, parse_mode="html")

LIBGEN_URL = 'https://libgen.is/search.php'
LIBGEN_MIRRORS = [
    'http://gen.lib.rus.ec/search.php',
    'http://gen.lib.rus.ec/search.php',
    'http://libgen.rs/search.php'
]

BOOK_TEXT_TEMPLATE = '''👨‍🏫Author: <i>{author}</i>\n
📝Title: <b>{title}</b>\n
📹Size: <u>{size}</u>\n
🔍Type: <b>{file}</b>\n
💡Year: <i>{year}</i>
'''

BOOK_TEXT_TEMPLATE_I = '''👨‍🏫Author: {author}\n
📝Title: {title}\n
📹Size: {size}\n
🔍Type: {file}\n
💡Year: {year}
'''

users = {}

def send_request(url, url_params=None):
    res = requests.get(url, params=url_params)
    if res.status_code == 200:
        return res.text
    try:
        for mirror in LIBGEN_MIRRORS:
            res = requests.get(mirror, params=url_params)
            if res.status_code == 200:
                return res.text
    except:
        pass

    return None

def get_file_url(mirror):
    page = send_request(mirror)
    if not page:
        return None
    soup = BeautifulSoup(page, features='html.parser')
    a = soup.find('a')
    h1 = soup.find('h1')
    url = a.get('href') if a else None
    file_name = h1.get_text() if h1 else None
    return url, file_name


def download_book(url, file_name, chat_id, message_id, query=None):
    bot.edit_message_text("<i>⬇️Downloading...\n\nPlease wait a moment✍️</i>", chat_id=chat_id, message_id=message_id)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        prev = -1      
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total) * 100
                    tmp = (percent // 10) * 5
                    if percent and tmp != prev:
                        try:
                            bot.edit_message_text("<b>💡Downloaded: {:.2f}%📝</b>".format(percent), chat_id=chat_id, message_id=message_id)                          
                        except Exception as e:
                            bot.send_message(chat_id, "An error occurred:(")
                    prev = tmp      
    except requests.exceptions.RequestException as e:
        bot.edit_message_text("Unable to download...", chat_id=chat_id, message_id=message_id)

def get_books(html):
    books = []
    soup = BeautifulSoup(html, features='html.parser')    
    table = soup.find('table', class_='c')
    rows = table.find_all('tr')
    for i, row in enumerate(rows):
        if len(books) == 10:
            break
        if i != 0:
            tds = row.find_all('td')
            book = {}
            for j, td in enumerate(tds):
                if j == 0 or j == 5:
                    continue
                elif j == 1:
                    book['author'] = td.get_text()
                elif j == 2:
                    book['title'] = td.find('a').get_text()
                elif j == 3:
                    book['publisher'] = td.get_text()
                elif j == 4:
                    book['year'] = td.get_text()
                elif j == 6:
                    book['language'] = td.get_text()
                elif j == 7:
                    book['size'] = td.get_text()
                elif j == 8:
                    book['file'] = td.get_text()
                else:
                    text = td.find('a').get_text()
                    link = td.find('a').get('href')
                    if text.lower() == '[edit]':
                        continue
                    if 'link' not in book:
                        book['link'] = link

            if 'mb' in book['size'].lower():
                size = float(book['size'].split()[0])
                if size > 50:
                    continue
            if book and book not in books:
                books.append(book)

    return books[:10]

def send_file(callback):
    query = callback
    data = query.data.split('&')
    link = f'http://library.lol/main/{data[0].split("_")[1]}'   
    msg = bot.send_message(callback.message.chat.id, "🔍Going to download...⬇️")
    url, file_name = get_file_url(link)
    unique = "books"
    unique_file_name = '-'.join(file_name.lower().split())
    file_type = data[1].split('=')[1]
    unique_file_name = f'books/{unique_file_name}-{unique}.{file_type}'
    download_book(url, unique_file_name, query=query, chat_id=callback.message.chat.id, message_id=msg.message_id)
    if file_name.split('.')[-1] != file_type:
        file_name = f'{file_name}.{file_type}'  
    bot.send_chat_action(callback.message.chat.id, "upload_document")
    
    if os.path.exists(unique_file_name):
        users[callback.from_user.id]["queue"] = False
        bot.send_document(callback.message.chat.id, document=open(unique_file_name, 'rb'), visible_file_name=file_name)        
        try:
            os.remove(unique_file_name)  
        except Exception as e:
            print("Error file:", e)
    else:
        bot.send_message(callback.message.chat.id, "An error occurred:(")

    return 1

def search_book(name):
    url_params = {
        'req': name,
        'res': 25,
        'view': 'simple',
        'column': 'def',
        'phrase': 1,
        'sort': 'year',
        'sortmode': 'DESC',
        'open': ()
    }

    response = send_request(LIBGEN_URL, url_params)
    if not response:
        return []
    books = get_books(response)
    return books
    
@bot.inline_handler(lambda query: True)
def handle_inline_query(query):
    books = search_book(str(query.query))
    try:        
        results = []
        for id, data in enumerate(books):
        	button_data = f'link_{data["link"].split("/")[-1]}&file={data["file"]}'
        	keyboard = InlineKeyboardMarkup(row_width=1)
        	keyboard.add(InlineKeyboardButton("✨My Updates✨", "t.me/mt_projectz"))
        	text = "Search result:\n\n"
        	text+=BOOK_TEXT_TEMPLATE_I.format(**data)
        	results.append(
               InlineQueryResultArticle(
                id=id,
                title=data["title"],
                thumbnail_url="https://t.me/Oro_Tech_Tips/892",
                reply_markup=keyboard,
                description=f"Size: {data['size']} || Author: {data['author']} || Year: {data['year']}",
                input_message_content=types.InputTextMessageContent(message_text=text),
         )
        )        
        bot.answer_inline_query(query.id, results)

    except Exception as e:
        pass
    
def search_book_handler(message):
    msg = bot.reply_to(message, "<i>Looking for this book...🔍</i>")
    text = message.text
    books = search_book(text)    
    if not books:
        bot.send_message(message.chat.id, "An error occurred: Book not found.")
        return 1    
    bot.set_state(message.from_user.id, "search", message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    	data["result"] = books
    keyboards = []
    
    markup = InlineKeyboardMarkup()
    for i, book in enumerate(books[:1]):      
        response_text = ''
        response_text += BOOK_TEXT_TEMPLATE.format(**book)
        response_text += '\n'

        button_data = f'link_{book["link"].split("/")[-1]}&file={book["file"]}'   
    markup.add(InlineKeyboardButton("⬇️Download⬇️", callback_data=button_data), InlineKeyboardButton("⏩Next", callback_data="page_2"))
    markup.add(InlineKeyboardButton("❎Cancel❎", callback_data="cancel"))
    bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"<b>{len(books)} books found for this search🔍</b>")    
    bot.send_message(message.chat.id,
        response_text, reply_markup=markup)
    return 1

@bot.message_handler(commands=["start"])
def start(message):
	user = DB().find_user(user_id=int(message.from_user.id))
	if user:
		accepted = DB().check_accept(int(message.from_user.id))
		if accepted:
			bot.send_message(message.chat.id, utility.WELCOME_MSG.format(message.from_user.first_name, bot.get_me().first_name), reply_markup=buttons.welcome_btns())
		else:
			return bot.send_message(message.chat.id, utility.DISCLAIMER_MSG, reply_markup=buttons.tos_btn())	
	else:
		DB().save_user(user_id=message.from_user.id)
		return bot.send_message(message.chat.id, utility.DISCLAIMER_MSG, reply_markup=buttons.tos_btn())		

@bot.message_handler(commands=["stats"])
def getStats(message):
	is_admin = DB().is_admin(message.from_user.id)
	if is_admin:
		bot.send_message(message.chat.id, f"Total users: {DB().get_stats()}")
	else:
		pass

@bot.message_handler(func=lambda message: True)
def handle_message(message):
	if bot.get_chat_member("@mt_projectz", message.from_user.id).status == "left":
		return bot.send_message(message.chat.id, utility.SUB_MSG.format(message.from_user.first_name))
	if "Search result:" in message.text:
		return 
	user_id = message.from_user.id
	accepted = DB().check_accept(int(message.from_user.id))
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
            response_text = ""
            response_text += BOOK_TEXT_TEMPLATE.format(**book)
            response_text += ''
            button_data = f'link_{book["link"].split("/")[-1]}&file={book["file"]}'
            if page > 1:
                buttons.append(InlineKeyboardButton("⏪Back", callback_data=f"page_{page - 1}"))
            if len(books) > end:
                buttons.append(InlineKeyboardButton("⏩Next", callback_data=f"page_{page + 1}"))
            buttons.append(InlineKeyboardButton("⬇️Download⬇️", callback_data=button_data))
            buttons.append(InlineKeyboardButton("❎Cancel❎", callback_data="cancel"))
            markup.add(*buttons)
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
	if bot.get_chat_member("@mt_projectz", callback.from_user.id).status == "left":
		return bot.send_message(callback.message.chat.id, utility.SUB_MSG.format(callback.from_user.first_name))
	bot.delete_message(callback.message.chat.id, callback.message.message_id)
	user_id = callback.from_user.id
	if user_id in users:
		if users[user_id]["queue"] == True:
			return bot.send_message(callback.message.chat.id, "<b>Let that book be downloaded before downloading another book:)</b>")
		else:
			users[user_id] = {"queue": True}
			send_file(callback)
	else:
		users[user_id] = {"queue": True}
		send_file(callback)
	

@bot.callback_query_handler(func = lambda callback: callback.data.startswith("cancel"))
def ans_c(callback):
	bot.answer_callback_query(callback.id, "lol")
	state = bot.get_state(callback.from_user.id, callback.message.chat.id)
	if state:
		bot.delete_state(callback.from_user.id, callback.message.chat.id)
		bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Cancelled.")
	else:
		bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Cancelled.")

@bot.callback_query_handler(func = lambda callback: True)
def ans(callback):
	if callback.data == "continue":
		DB().accepted_tos(callback.from_user.id)
		return bot.edit_message_text(utility.WELCOME_MSG.format(callback.from_user.first_name, bot.get_me().first_name), chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=buttons.welcome_btns())
	if callback.data == "help":
		bot.edit_message_text(utility.HELP_MSG.format(bot.get_me().username), chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=buttons.back_btn())	
	if callback.data == "back":
		bot.edit_message_text(utility.WELCOME_MSG.format(callback.from_user.first_name, bot.get_me().first_name), chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=buttons.welcome_btns())
	if callback.data == "tos":
		bot.edit_message_text(utility.DISCLAIMER_MSG, chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=buttons.back_btn())	
		
bot.add_custom_filter(custom_filters.StateFilter(bot))
