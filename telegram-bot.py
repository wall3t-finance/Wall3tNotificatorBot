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
    if user_id in user_data:
        user_data.pop(user_id)
        print(f"Notifications stopped for user with id {user_id}")
        print(user_data)
        bot.send_message(message.chat.id, "Notifications stopped")
    else:
        bot.send_message(message.chat.id, "You are not receiving notifications")

@bot.message_handler(func=lambda message: True)
def save_contract_address(message):
    user_id = message.from_user.id
    user_data[user_id] = {"contract_address": message.text, "message_chat_id": message.chat.id, "last_hash": None}

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
        for user_id in user_data:
            try:
                print(f"Checking for user with id {user_id}...")
                contract_address = user_data[user_id]["contract_address"]
                message_chat_id = user_data[user_id]["message_chat_id"]
                response = utils.get_last_movement(contract_address, 5)
                if response == "Error":
                    print("Error fetching information about the contract. Please try again.")
                    bot.send_message(message_chat_id, "Error fetching information about the contract. Please try again.")
                elif user_data[user_id]["last_hash"] == None:
                    print("First time checking for transactions")
                    user_data[user_id]["last_hash"] = response[0]["hash"]
                elif response[0]["hash"] != user_data[user_id]["last_hash"]:
                    print("New transaction found!")
                    n = 0
                    while n < len(response) and response[n]["hash"] != user_data[user_id]["last_hash"]:
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
                        # print(formatted_json)
                        print("🆕*NEW TRANSACTION*🆕")
                        bot.send_message(message_chat_id, formatted_json, parse_mode="Markdown")
                        n += 1
                    user_data[user_id]["last_hash"] = response[0]["hash"]
                else:
                    print("No new transactions found")
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
