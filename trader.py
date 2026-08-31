import os
import ccxt
import json
from dotenv import load_dotenv
import config

load_dotenv()

class KuCoinTrader:
    def __init__(self):
        # 1. Exchange Setup with Rate Limit & Timeout Fixes
        self.exchange = ccxt.kucoin({
            'apiKey': os.getenv('KUCOIN_API_KEY', ''),
            'secret': os.getenv('KUCOIN_SECRET', ''),
            'password': os.getenv('KUCOIN_PASSPHRASE', ''),
            'enableRateLimit': True,
            'timeout': 30000,
        })
        
        self.paper_trading = getattr(config, 'PAPER_TRADING', True)
        self.portfolio_file = 'paper_portfolio.json'
        self.portfolio = self.load_portfolio()

    def load_portfolio(self):
        """Load paper portfolio or create a fresh one if missing"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Fresh Default State ($5000 USDT)
        initial_balance = getattr(config, 'INITIAL_PAPER_BALANCE', 5000)
        return {
            "usdt_balance": initial_balance,
            "btc_balance": 0.0,
            "in_position": False,
            "buy_price": 0.0,
            "trade_history": []
        }

    def save_portfolio(self):
        """Save paper portfolio state"""
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=4)

    def fetch_current_price(self, symbol="BTC/USDT"):
        """Fetch single pair ticker safely"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return None

    def execute_paper_trade(self, action, current_price, symbol="BTC/USDT"):
        """Execute buy/sell trade and update portfolio state"""
        action = str(action).upper()
        max_amount = getattr(config, 'MAX_TRADE_AMOUNT', 1000)
        
        if action == "BUY" and not self.portfolio.get("in_position", False):
            if self.portfolio["usdt_balance"] >= max_amount:
                crypto_bought = max_amount / current_price
                self.portfolio["usdt_balance"] -= max_amount
                self.portfolio["btc_balance"] += crypto_bought
                self.portfolio["in_position"] = True
                self.portfolio["buy_price"] = current_price
                
                self.portfolio["trade_history"].append({
                    "Type": "BUY",
                    "Symbol": symbol,
                    "Price": f"${current_price}",
                    "Amount": f"${max_amount}",
                    "PnL_Raw": 0.0
                })
                self.save_portfolio()
                
        elif action == "SELL" and self.portfolio.get("in_position", False):
            crypto_qty = self.portfolio["btc_balance"]
            sell_value = crypto_qty * current_price
            cost_basis = crypto_qty * self.portfolio["buy_price"]
            pnl = sell_value - cost_basis
            
            self.portfolio["usdt_balance"] += sell_value
            self.portfolio["btc_balance"] = 0.0
            self.portfolio["in_position"] = False
            
            self.portfolio["trade_history"].append({
                "Type": "SELL",
                "Symbol": symbol,
                "Price": f"${current_price}",
                "Amount": f"${round(sell_value, 2)}",
                "PnL": f"${round(pnl, 2)}",
                "PnL_Raw": pnl
            })
            self.portfolio["buy_price"] = 0.0
            self.save_portfolio()
            
        return self.portfolio

# =========================================================
# DASHBOARD EXPORTED FUNCTIONS
# =========================================================
_trader_instance = KuCoinTrader()

def execute_trade(action, price=None, symbol="BTC/USDT"):
    """Matches dashboard signature: execute_trade(action, price, symbol=...)"""
    if price is None or price <= 0:
        price = _trader_instance.fetch_current_price(symbol) or 0.0
        
    return _trader_instance.execute_paper_trade(action, price, symbol)

def calculate_pnl_stats(history=None):
    """Matches dashboard signature: returns total_pnl, wins, losses, win_rate"""
    if history is None:
        history = _trader_instance.portfolio.get("trade_history", [])
        
    pnl_list = [item.get("PnL_Raw", 0.0) for item in history if "PnL_Raw" in item and item.get("Type") == "SELL"]
    
    total_pnl = round(sum(pnl_list), 2)
    wins = len([p for p in pnl_list if p > 0])
    losses = len([p for p in pnl_list if p < 0])
    total_trades = wins + losses
    win_rate = round((wins / total_trades * 100), 1) if total_trades > 0 else 0.0
    
    return total_pnl, wins, losses, win_rate