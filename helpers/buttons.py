from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def welcome_btns():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("✨My Channel✨", url="t.me/mt_projectz"),InlineKeyboardButton("♻️Get Help♻️", callback_data="help"))
	keyboard.add(InlineKeyboardButton("👥Support Group👥", url="t.me/mt_projectzchat"))
	keyboard.add(InlineKeyboardButton("✍️Terms of service✍️", callback_data="tos"))
	return keyboard
	
def tos_btn():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("✨Continue✨", callback_data="continue"))	
	return keyboard

def back_btn():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("🔙Back", callback_data="back"))
	return keyboard
