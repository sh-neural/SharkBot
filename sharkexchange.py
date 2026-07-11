import os
import requests
import hmac
import hashlib
import time
import json
from config import base_url
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")

def generate_signature(api_secret, data_to_sign):
  return hmac.new(api_secret.encode('utf-8'), data_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

#FUNCTION TO GET WALLET DETAILS

def get_futures_wallet_details():
  endpoint = "/v1/wallet/futures-wallet/details"

  # Generate the current timestamp
  timestamp = str(int(time.time() * 1000))

  # Optional parameters with timestamp
  params = {
      'marginAsset': 'INR',
      'timestamp': timestamp
  }

  query_string = f"marginAsset={params['marginAsset']}&timestamp={params['timestamp']}"

  # Generate the signature (ensure `generate_signature` is properly defined)
  signature = generate_signature(api_secret, query_string)

  # Headers for the GET request
  headers = {
      'api-key': api_key,
      'signature': signature
  }

  # Construct the full URL
  wallet_details_url = f"{base_url}{endpoint}?{query_string}"

  try:
      # Send the GET request to fetch the futures wallet details
      response = requests.get(wallet_details_url, headers=headers)
      response.raise_for_status()  # Raises an error for 4xx/5xx responses
      response_data = response.json()
      print('Futures wallet details:', json.dumps(response_data, indent=4))
  except requests.exceptions.HTTPError as err:
      print(f"Failed {response.status_code}: {response.text}")
  except Exception as e:
      print(f"An unexpected error occurred: {str(e)}")

#FUNCTION TO PLACE A NEW ORDER

def place_order():
    # Generate the current timestamp in milliseconds
    timestamp = str(int(time.time() * 1000))

    # Define the order parameters
    params = {
        'timestamp': timestamp,        # Current timestamp in milliseconds
        'placeType': 'ORDER_FORM',     # Type of order placement, e.g., 'ORDER_FORM'
        'quantity': 0.1,             # Quantity of the asset to trade
        'side': 'BUY',                 # Order side, either 'BUY' or 'SELL'
        'symbol': 'BTCUSDT',           # Trading pair, e.g., Bitcoin to USDT
        'type': 'MARKET',              # Order type, either 'MARKET' or 'LIMIT'
        'reduceOnly': False,           # Whether to reduce an existing position only
        'marginAsset': 'INR',          # The asset used as margin (INR in this case)
        'deviceType': 'WEB',           # Device type (e.g., WEB, MOBILE)
        'userCategory': 'EXTERNAL',    # User category (e.g., EXTERNAL, INTERNAL)
        'price': 50000,                # Price for the limit order (included here but irrelevant for market orders)
    }

    # Convert the parameters to a JSON string to sign
    data_to_sign = json.dumps(params, separators=(',', ':'))

    # Generate the signature for authentication
    signature = generate_signature(api_secret, data_to_sign)

    # Define the headers including the API key and the signature
    headers = {
        'api-key': api_key,
        'signature': signature,
    }

    try:
        # Send the POST request to place the order
        response = requests.post(f'{base_url}/v1/order/place-order', json=params, headers=headers)

        # Raise an HTTPError if the response status is 4xx or 5xx
        response.raise_for_status()

        # Parse the JSON response data
        response_data = response.json()

        # Print the success message with the order details
        print('Order placed successfully:', json.dumps(response_data, indent=4))

    except requests.exceptions.HTTPError as err:
        # Handle HTTP errors specifically
        print(f"Error: {err.response.text if err.response else err}")

    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {str(e)}")

#FUNCTION TO SET TARGET AND SL

def split_tp_sl():
    position_id = input("Enter the positionId: ")
    tp_quantity_input = input("Enter the TP quantity: ")
    tp_price_input = input("Enter the TP price: ")
    sl_quantity_input = input("Enter the SL quantity: ")
    sl_price_input = input("Enter the SL price: ")

    add_margin_url = "https://api.sharkexchange.in/v2/order/split-tp-sl"

    try:
        tp_quantity = int(tp_quantity_input)
    except ValueError:
        tp_quantity = float(tp_quantity_input)

    try:
        tp_price = int(tp_price_input)
    except ValueError:
        tp_price = float(tp_price_input)

    try:
        sl_quantity = int(sl_quantity_input)
    except ValueError:
        tp_price = float(sl_quantity_input)

    try:
        sl_price = int(sl_price_input)
    except ValueError:
        sl_price = float(sl_price_input)

    timestamp = str(int(time.time() * 1000))

    params = {
        'positionId': position_id,
        'splitTakeProfitOrders':[{
          'quantity': tp_quantity,
          'price' : tp_price
        }],
        splitStopLossOrders:[{
          'quantity': sl_quantity,
          'price' : sl_price
        }],
        'timestamp': timestamp
    }

    data_to_sign = json.dumps(params, separators=(',', ':'))
    signature = generate_signature(api_secret, data_to_sign)

    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'signature': signature,
    }

    try:
        response = requests.post(add_margin_url, json=params, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print('Margin added successfully:', json.dumps(response_data, indent=4))

    except requests.exceptions.HTTPError as err:
        print(f"Failed {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
