import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# TRADING BOT CONFIGURATION (DEMO HIGH CAPITAL)
# ==========================================

PAPER_TRADING = True         # Demo / Paper Trading active

# 1. Total Portfolio Balance (Demo Capital)
#1. Total Portfolio Balance (Variable Name Fixed)
INITIAL_PAPER_BALANCE = 5000       # $5,000 Virtual Balance  # $5,000 Virtual Balance se start karega

# 2. Per Trade Sizing (Thousands mein trade)
MAX_TRADE_AMOUNT = 3500     # Har trade $1,000 USDT ki lagegi

# 3. Risk Management (Tight Stop Loss, High Reward)
STOP_LOSS_PERCENT = 0.8      # Chota Stop Loss (0.8%)
TAKE_PROFIT_PERCENT = 3.5    # Bada Profit Target (3.5%)

# Technical Thresholds
RSI_BUY_THRESHOLD = 35
RSI_SELL_THRESHOLD = 68

EXCHANGE_NAME = "kucoin"