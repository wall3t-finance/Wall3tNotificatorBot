import telebot, os, threading, time
from telebot import types
from dotenv import load_dotenv
import utils

load_dotenv("access-token.env")
BOT_TOKEN = os.getenv("TELEGRAM-BOT-ACCESS-TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
global is_running
is_running = False

# Dictionary to store user data, including their contract address
user_data = {}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")
    bot.send_message(message.chat.id, "Please enter a public contract address:")

@bot.message_handler(commands=['stop'])
def stop_notifications(message):
    user_id = message.from_user.id

    if user_id not in user_data or not user_data[user_id]["contract_addresses"]:
        bot.send_message(message.chat.id, "You are not tracking any contract addresses.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard_items = [types.KeyboardButton(address) for address in user_data[user_id]["contract_addresses"]]
    keyboard_items.append(types.KeyboardButton("Delete All"))
    markup.add(*keyboard_items)

    bot.send_message(message.chat.id, "Select the contract address you want to stop tracking:", reply_markup=markup)
    bot.register_next_step_handler(message, delete_contract_address)

def delete_contract_address(message):
    user_id = message.from_user.id
    selected_option = message.text

    if selected_option == "Delete All":
        user_data[user_id]["contract_addresses"] = []
        user_data[user_id]["last_hashes"] = {}
        bot.send_message(message.chat.id, "All contract addresses have been deleted.")
    elif selected_option in user_data[user_id]["contract_addresses"]:
        user_data[user_id]["contract_addresses"].remove(selected_option)
        user_data[user_id]["last_hashes"].pop(selected_option, None)
        bot.send_message(message.chat.id, f"Contract address {selected_option} has been deleted.")
    else:
        bot.send_message(message.chat.id, "Invalid choice. Please select a valid contract address or 'Delete All'.")

    bot.send_message(message.chat.id, "Keyboard removed.", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: True)
def save_contract_address(message):
    user_id = message.from_user.id
    contract_address = message.text
    if user_id not in user_data:
        print("New user")
        user_data[user_id] = {"contract_addresses": [contract_address], "message_chat_id": message.chat.id, "last_hashes": {}}
    else:
        print("Existing user")
        user_data[user_id]["contract_addresses"].append(contract_address)

    bot.send_message(message.chat.id, f"Contract address {user_data[user_id]['contract_address']} saved")
    print(user_data)
    if not is_running:
        thread = threading.Thread(target=handle_user_choice)
        thread.daemon = True
        thread.start()

def handle_user_choice():
    is_running = True

    while len(user_data) > 0:
        print("\nChecking for new transactions...")
        for user_id, user_info in user_data.items():
            try:
                print(f"Checking for user with id {user_id}...")
                for contract_address in user_info["contract_addresses"]:
                    contract_data = user_info["last_hashes"].get(contract_address, {})
                    message_chat_id = user_info["message_chat_id"]

                    response = utils.get_last_movement(contract_address, 5)
                    if response == "Error":
                        print("Error fetching information about the contract. Please try again.")
                        bot.send_message(message_chat_id, "Error fetching information about the contract. Please try again.")
                    elif "last_hash" not in contract_data:
                        print("First time checking for transactions")
                        contract_data["last_hash"] = response[0]["hash"]
                    elif response[0]["hash"] != contract_data["last_hash"]:
                        print("New transaction found!")
                        n = 0
                        while n < len(response) and response[n]["hash"] != contract_data["last_hash"]:
                            formatted_json = f"\t🆕*NEW TRANSACTION*🆕\n" \
                                f"🔗 *Block Number*: {response[n]['blockNumber']}\n⏰ *Timestamp*: {response[n]['timeStamp']} seconds\n📜 *Hash*: {response[n]['hash']}\n" \
                                f"🔑 *Nonce*: {response[n]['nonce']}\n🔗 *Block Hash*: {response[n]['blockHash']}\n" \
                                f"🔍 *Transaction Index*: {response[n]['transactionIndex']}\n👤 *From*: {response[n]['from']}\n" \
                                f"💰 *To*: {response[n]['to']}\n💲 *Value*: {response[n]['value']} Wei\n⛽ *Gas*: {response[n]['gas']} Wei\n" \
                                f"💹 *Gas Price*: {response[n]['gasPrice']} Wei\n❌ *Error*: {'❌' if response[n]['isError'] == '1' else '✅'}\n" \
                                f"🛡️ *Receipt Status*: {'✅' if response[n]['txreceipt_status'] == '1' else '❌'}\n" \
                                f"🏦 *Contract Address*: {response[n]['contractAddress']}\n" \
                                f"📈 *Cumulative Gas Used*: {response[n]['cumulativeGasUsed']} Wei\n⛽ *Gas Used*: {response[n]['gasUsed']} Wei\n" \
                                f"🔒 *Confirmations*: {response[n]['confirmations']}\n🔍 *Method ID*: {response[n]['methodId']}\n" \
                                f"📜 *Function Name*: {response[n]['functionName']}\n"
                            print("🆕*NEW TRANSACTION*🆕")
                            bot.send_message(message_chat_id, formatted_json, parse_mode="Markdown")
                            n += 1
                        contract_data["last_hash"] = response[0]["hash"]
                        user_info["last_hashes"][contract_address] = contract_data
                    else:
                        print(f"No new transactions found for {contract_address}")
            except Exception as e:
                print(f"Error:\n{e}")
            
        print("Sleeping for 5 seconds")
        time.sleep(5)

    print("No users left")
    is_running = False


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, "This is not a valid command. Please try again.")


if __name__ == "__main__":
    bot.infinity_polling()
