import requests, os
from web3 import Web3
from dotenv import load_dotenv

def get_daily_horoscope(sign: str, day: str) -> dict:
    """Get daily horoscope for a zodiac sign.

    Keyword arguments:
    sign:str - Zodiac sign
    day:str - Date in format (YYYY-MM-DD) OR TODAY OR TOMORROW OR YESTERDAY
    Return:dict - JSON data
    """
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)

    return response.json()

def get_last_movement(contract_address: str, num_transactions = 10) -> dict:
    """Get last movement of a contract.

    Keyword arguments:
    contract_address:str - Contract address
    num_transactions:int - Number of transactions to fetch (default: 10)
    Return:dict - JSON data
    """
    load_dotenv("access-token.env")
    
    url = "https://api-sepolia.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": contract_address,
        "startblock": 0,  # Replace with your start block number
        "endblock": 99999999,  # Replace with your end block number
        "page": 1,  # Page number (1 for the first page)
        "offset": num_transactions,
        "sort": "desc",  # Sort by descending to get the latest transactions
        "apikey": os.getenv("ETHERSCAN-API-KEY")
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            return data["result"]
        else:
            print("No transaction data found.")
    else:
        print("Failed to fetch data. Check your API key and request parameters.")

    return "Error"


if __name__ == "__main__":
    contract = input("Enter contract address: ")
    print(get_last_movement(contract))