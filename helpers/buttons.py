from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def welcome_btns():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("Find Books 🔍", switch_inline_query_current_chat="JavaScript"))
	keyboard.add(InlineKeyboardButton("See Help ♻️", callback_data="help"))
	return keyboard
	
def tos_btn():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("Continue ✨", callback_data="continue"))	
	return keyboard

def back_btn():
	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton("Go back 🔙", callback_data="back"))
	return keyboard
