import telebot, os
from telebot import types
from dotenv import load_dotenv

load_dotenv("access-token.env")
BOT_TOKEN=os.getenv("TELEGRAM-BOT-ACCESS-TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Create a dictionary to store the possible options for each menu
options_dict = {
    "main_menu": ["Option 1", "Option 2", "Option 3"],
    "submenu_option3": ["Suboption 1", "Suboption 2", "Back to Main Menu"],
}

# Create a function to build an inline keyboard from a list of options
def build_keyboard(options):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        callback_data = option.lower().replace(" ", "_")
        button = types.InlineKeyboardButton(option, callback_data=callback_data)
        keyboard.add(button)
    return keyboard

# Define a function to handle callback data
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    callback_data = call.data
    chat_id = call.message.chat.id

    if callback_data in [option.lower().replace(" ", "_") for option in options_dict["main_menu"]]:
        if callback_data == "option_3":
            print("Option 3 selected")
            # Show submenu options for Option 3
            submenu_options = options_dict["submenu_option3"]
            submenu_keyboard = build_keyboard(submenu_options)
            bot.send_message(chat_id, "Choose a sub-option:", reply_markup=submenu_keyboard)
        else:
            bot.send_message(chat_id, f"You selected {callback_data}.")

    elif callback_data in [option.lower().replace(" ", "_") for option in options_dict["submenu_option3"]]:
        if callback_data == "back_to_main_menu":
            # Show the main menu options
            main_menu_options = options_dict["main_menu"]
            main_menu_keyboard = build_keyboard(main_menu_options)
            bot.send_message(chat_id, "Back to Main Menu. Choose an option:", reply_markup=main_menu_keyboard)
        else:
            bot.send_message(chat_id, f"You selected {callback_data}.")

# Handle the /start command to send the main menu
@bot.message_handler(commands=['start'])
def send_main_menu(message):
    main_menu_options = options_dict["main_menu"]
    main_menu_keyboard = build_keyboard(main_menu_options)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=main_menu_keyboard)

# Start the bot and listen for messages and callbacks
bot.infinity_polling()

