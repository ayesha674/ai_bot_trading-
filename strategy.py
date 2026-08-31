import os
import json
import requests
import numpy as np

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        return 100.0
        
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0:
        return 100.0
        
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def fetch_crypto_news(symbol="BTC"):
    """
    CryptoPanic public feed se top breaking headlines fetch karta hai.
    """
    try:
        coin = symbol.split('/')[0].upper()
        url = f"https://cryptopanic.com/api/v1/posts/?auth_token=free&currencies={coin}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get('results', [])
            titles = [post['title'] for post in results[:5]]
            if titles:
                return " | ".join(titles)
    except Exception:
        pass
    return "Market moving standard parameters without high panic news."

def analyze_news_sentiment(news_text, gemini_key):
    """
    Gemini AI news context read karke Sentiment Score (-1.0 to +1.0) provide karta hai.
    """
    if not gemini_key or "without high panic" in news_text:
        return 0.0, "NEUTRAL (No News Impact)"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        prompt = f"""
        Analyze these crypto breaking news for market direction:
        "{news_text}"

        Determine if news is highly bullish, bearish, or neutral.
        Respond STRICTLY in JSON format:
        {{"score": 0.5, "reason": "Short summary here"}}
        where score is between -1.0 (Very Bearish) and +1.0 (Very Bullish).
        """
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            res_text = response.json()['candidates'][0]['content']['parts'][0]['text']
            clean_json = res_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            return float(data.get("score", 0.0)), data.get("reason", "Neutral sentiment")
    except Exception:
        pass
    return 0.0, "NEUTRAL (Analysis Skipped)"

def analyze_market_signal(ohlcv_15m, ohlcv_1h, gemini_key=None, symbol="BTC/USDT"):
    closes_15m = [candle[4] for candle in ohlcv_15m]
    closes_1h = [candle[4] for candle in ohlcv_1h]
    
    current_price = closes_15m[-1]
    rsi_15m = calculate_rsi(closes_15m, 14)
    
    ema_20 = round(float(np.mean(closes_15m[-20:])), 2)
    ema_50 = round(float(np.mean(closes_15m[-50:])), 2)
    ema_1h_50 = float(np.mean(closes_1h[-50:]))
    
    trend_1h = "BULLISH 📈" if current_price > ema_1h_50 else "BEARISH 📉"
    
    # Base Technical Signal
    signal = "HOLD"
    if current_price > ema_20 and rsi_15m < 65 and trend_1h == "BULLISH 📈":
        signal = "BUY"
    elif current_price < ema_20 or rsi_15m > 70:
        signal = "SELL"
        
    # AI News & Current Affairs Filter
    news_headlines = fetch_crypto_news(symbol)
    news_score, news_reason = analyze_news_sentiment(news_headlines, gemini_key)
    
    # Combine Technical + News Affairs
    if news_score < -0.4 and signal == "BUY":
        signal = "HOLD (Negative News Risk ⚠️)"
    elif news_score > 0.6 and rsi_15m < 60:
        signal = "STRONG BUY (Bullish News 🚀)"
    elif news_score < -0.6:
        signal = "SELL (Bearish News Panic 🔴)"
        
    return {
        "price": current_price,
        "rsi": rsi_15m,
        "ema_20": ema_20,
        "ema_50": ema_50,
        "trend_1h": trend_1h,
        "signal": signal,
        "news_score": news_score,
        "news_reason": news_reason,
        "news_headlines": news_headlines
    }