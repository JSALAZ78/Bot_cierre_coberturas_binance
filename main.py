import config  # Este archivo debe contener tus claves de API
from binance.client import Client
from binance.enums import *
import time

client = Client(config.API_KEY, config.API_SECRET, tld='com')

def get_open_orders(symbol):
    return client.futures_get_open_orders(symbol=symbol)

def cancel_order(symbol, order_id):
    return client.futures_cancel_order(symbol=symbol, orderId=order_id)

def get_current_price(symbol):
    ticker = client.futures_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def print_distances(symbol, tp_price, coverage_price):
    current_price = get_current_price(symbol)
    tp_distance = abs(current_price - tp_price)
    coverage_distance = abs(current_price - coverage_price)
    print(f"Current Price: {current_price}, TP Distance: {tp_distance}, Coverage Distance: {coverage_distance}")

def monitor_orders(symbol, tp_order_id, coverage_order_id):
    tp_price = None
    coverage_price = None

    while True:
        open_orders = get_open_orders(symbol)
        
        tp_active = any(order['orderId'] == tp_order_id for order in open_orders)
        coverage_active = any(order['orderId'] == coverage_order_id for order in open_orders)
        
        for order in open_orders:
            if order['orderId'] == tp_order_id:
                tp_price = float(order['price'])
            if order['orderId'] == coverage_order_id:
                coverage_price = float(order['stopPrice'])
        
        if tp_price is not None and coverage_price is not None:
            print_distances(symbol, tp_price, coverage_price)
        
        if not tp_active and coverage_active:
            print("Take Profit reached, closing coverage order")
            cancel_order(symbol, coverage_order_id)
            break
        
        if coverage_active and not tp_active:
            print("Coverage activated, closing Take Profit order")
            cancel_order(symbol, tp_order_id)
            break
        
        time.sleep(180)  # Espera 3 minutos antes de volver a comprobar

# Configura tus órdenes y símbolo aquí
symbol = "BTCUSDT"
tp_order_id = '1234'  # Reemplaza con tu ID de orden TP
coverage_order_id = '1234'  # Reemplaza con tu ID de orden de cobertura

monitor_orders(symbol, tp_order_id, coverage_order_id)

