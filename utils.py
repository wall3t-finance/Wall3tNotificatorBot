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
    headers = {
    'authority': 'apothem.xinfinscan.com',
    'accept': 'application/json, text/plain, */*',
    'access-control-allow-origin': '*',
    }

    params = {
        'page': '1',
        'limit': '20',
        'tx_type': 'all',
    }

    url = f"https://apothem.xinfinscan.com/api/txs/listByAccount/{contract_address}"

    response = requests.get(
        url=url,
        params=params,
        headers=headers,
    )

    if response.status_code == 200:
        data = response.json()
        if len(data["items"]) > 0:
            return data["items"]
        else:
            print("No transaction data found.")
            return data
    else:
        print("Failed to fetch data. Check your API key and request parameters.")

    return "Error"


if __name__ == "__main__":
    contract = input("Enter contract address: ")
    print(get_last_movement(contract))