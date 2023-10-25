import telebot, os, asyncio
from telebot import types
from dotenv import load_dotenv
import utils

load_dotenv("access-token.env")
BOT_TOKEN = os.getenv("TELEGRAM-BOT-ACCESS-TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

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
        bot.send_message(message.chat.id, "Notifications stopped")
    else:
        bot.send_message(message.chat.id, "You are not receiving notifications")

@bot.message_handler(func=lambda message: True)
def save_contract_address(message):
    user_id = message.from_user.id
    user_data[user_id] = {"contract_address": message.text, "message_chat_id": message.chat.id, "last_hash": None}

    bot.send_message(message.chat.id, f"Contract address {user_data[user_id]['contract_address']} saved")
    if not is_running:
        handle_user_choice_async


async def handle_user_choice_async():
    global is_running
    is_running = True

    while len(user_data) > 0:
        for user in user_data:
            contract_address = user["contract_address"]
            message_chat_id = user["message_chat_id"]
            response = await utils.get_last_movement_async(contract_address)
            if response == "Error":
                await bot.send_message(message_chat_id, "Error fetching information about the contract. Please try again.")
            elif user["last_input"] == None:
                user["last_input"] = response[0]["hash"]
                
            elif response[0]["hash"] != user["last_input"]:
                n = 0
                while response[n]["hash"] != user["last_input"]:
                    formatted_json = f"🔗 *Block Number*: {response[n]['blockNumber']}\n⏰ *Timestamp*: {response[n]['timeStamp']} seconds\n📜 *Hash*: {response[n]['hash']}\n" \
                        f"🔑 *Nonce*: {response[n]['nonce']}\n🔗 *Block Hash*: {response[n]['blockHash']}\n" \
                        f"🔍 *Transaction Index*: {response[n]['transactionIndex']}\n👤 *From*: {response[n]['from']}\n" \
                        f"💰 *To*: {response[n]['to']}\n💲 *Value*: {response[n]['value']} Wei\n⛽ *Gas*: {response[n]['gas']} Wei\n" \
                        f"💹 *Gas Price*: {response[n]['gasPrice']} Wei\n❌ *Error*: {'❌' if response[n]['isError'] == '1' else '✅'}\n" \
                        f"🛡️ *Receipt Status*: {'✅' if response[n]['txreceipt_status'] == '1' else '❌'}\n" \
                        f"🏦 *Contract Address*: {response[n]['contractAddress']}\n" \
                        f"📈 *Cumulative Gas Used*: {response[n]['cumulativeGasUsed']} Wei\n⛽ *Gas Used*: {response[n]['gasUsed']} Wei\n" \
                        f"🔒 *Confirmations*: {response[n]['confirmations']}\n🔍 *Method ID*: {response[n]['methodId']}\n" \
                        f"📜 *Function Name*: {response[n]['functionName']}\n"
                    print(formatted_json)
                    await bot.send_message(message_chat_id, formatted_json, parse_mode="Markdown")
                    n += 1
                user["last_input"] = response[0]["hash"]
        await asyncio.sleep(5)

    is_running = False

# Handle other messages
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


if __name__ == "__main__":
    bot.infinity_polling()
