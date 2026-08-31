import os
import time
import ccxt
from dotenv import load_dotenv
import config
from strategy import analyze_market_signal
from trader import execute_trade

load_dotenv()

api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True,
        'recvWindow': 60000
    }
})

def run_automated_bot():
    print("🚀 AI Crypto Trading Bot Started! Press Ctrl+C to Stop.\n")
    
    while True:
        try:
            # 1. Fetch Market Data
            ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=50)
            analysis = analyze_market_signal(ohlcv)
            
            # 2. Execute Strategy & Paper Trade
            portfolio = execute_trade(analysis['signal'], analysis['price'])
            
            # 3. Print Live Terminal Dashboard
            os.system('cls' if os.name == 'nt' else 'clear')  # Screen clear for clean view
            print("==================================================")
            print("          AI TRADING BOT (LIVE MONITOR)           ")
            print("==================================================")
            print(f" Mode            : {'[ DEMO / PAPER TRADING ]' if config.PAPER_TRADING else '[ REAL TRADING ]'}")
            print(f" BTC Price       : ${analysis['price']}")
            print(f" RSI Indicator   : {analysis['rsi']}")
            print(f" AI Decision     : [ {analysis['signal']} ]")
            print("--------------------------------------------------")
            print(f" USDT Balance    : ${round(portfolio['usdt_balance'], 2)}")
            print(f" BTC Balance     : {round(portfolio['btc_balance'], 6)} BTC")
            print(f" Active Trade    : {'YES' if portfolio['in_position'] else 'NO'}")
            print("==================================================")
            print("⏳ Scanning market again in 30 seconds...")
            
            # 30 seconds wait before next scan
            time.sleep(30)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped manually by user.")
            break
        except Exception as e:
            print(f"⚠️ Error occurred: {e}. Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    run_automated_bot()