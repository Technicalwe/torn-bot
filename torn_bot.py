import requests
import time
import schedule
import os

# Load API key from environment variable (better security)
API_KEY = os.getenv('TORN_API_KEY')

if not API_KEY:
    raise ValueError("Missing Torn API key! Set TORN_API_KEY as an environment variable.")

HEADERS = {'Authorization': f'Bearer {API_KEY}'}

def get_inventory():
    try:
        url = f'https://api.torn.com/user/?selections=inventory&key={API_KEY}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('inventory', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching inventory: {e}")
        return []

def buy_beer():
    try:
        url = f'https://api.torn.com/user/?selections=buyitem&key={API_KEY}'
        payload = {
            'item_id': 180,  # ✅ Correct ID for Beer Bottle
            'quantity': 100
        }
        response = requests.post(url, data=payload, headers=HEADERS)
        print(response.json())
        time.sleep(2)  # ⏳ Delay to avoid rate limit
    except requests.exceptions.RequestException as e:
        print(f"Error buying beer: {e}")

def sell_beer():
    inventory = get_inventory()
    market_count = 0
    
    for item in inventory:
        if item['ID'] == 180:  # ✅ Match with correct ID
            if market_count >= 100:
                print("Market listing limit reached. Stopping...")
                break

            try:
                url = f'https://api.torn.com/market/?selections=sellitem&key={API_KEY}'
                payload = {
                    'item_id': item['ID'],
                    'quantity': 1,
                    'price': 1000
                }
                response = requests.post(url, data=payload, headers=HEADERS)
                print(response.json())
                
                market_count += 1
                time.sleep(2)  # ⏳ Delay between sales to avoid rate limit
            except requests.exceptions.RequestException as e:
                print(f"Error selling beer: {e}")

def daily_task():
    inventory = get_inventory()
    beer_count = sum(1 for item in inventory if item['ID'] == 180)
    
    print(f"🍺 Current beer count: {beer_count}")

    if beer_count < 100:
        print("Buying more beer...")
        buy_beer()
    
    print("Selling beer...")
    sell_beer()

# Schedule the bot to run once a day at midnight Torn time (UTC)
schedule.every().day.at("00:00").do(daily_task)

print("🍺 Beer Bot is running...")

# Keep the bot running
while True:
    schedule.run_pending()
    time.sleep(60)
