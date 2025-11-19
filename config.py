# Trading Analytics Tool Configuration
# Copy this file to config.py and update with your credentials

# TradingView Credentials
TRADINGVIEW_USER = ""
TRADINGVIEW_PASS = ""
TRADINGVIEW_2FA_SECRET = ""

LIST_STRATEGY_SETTINGS={
    "xau-long": {
        "asset_name": "XAU (Gold)", 
        "strategy_name": "xau-long-bot", 
        "symbol": "FX:XAUUSD", 
        "target_criteria": {"total_trades_min": 105, "max_drawdown_max": 30}, 
        "time_backtest": "2009 => present", 
        "target_potential": {"total_trades_min": 30, "max_drawdown_max": 40},
        "prompt_template": {
            "context": "You are an AI agent specialized in PineScript code optimization for Gold (XAU) trading strategies.",
            "asset_description": "XAU can be long in some situations like:\n- trend following\n- safe haven demand\n- inflation hedge\n- technical breakouts",
            "optimization_focus": "Focus on Gold's unique characteristics: volatility patterns, safe-haven flows, and correlation with USD strength.",
            "risk_considerations": "Gold is sensitive to interest rates, inflation expectations, and geopolitical events. Consider these factors in your logic."
        }
    },
    "btc-long": {
        "asset_name": "BTC (Bitcoin)", 
        "strategy_name": "btc-long-bot", 
        "symbol": "OKX:BTCUSDT.P", 
        "target_criteria": {"total_trades_min": 25, "max_drawdown_max": 30}, 
        "time_backtest": "2019 => present", 
        "target_potential": {"total_trades_min": 20, "max_drawdown_max": 50},
        "prompt_template": {
            "context": "You are an AI agent specialized in PineScript code optimization for Bitcoin (BTC) long trading strategies.",
            "asset_description": "BTC can be long in some situations like:\n- momentum trading\n- breakout strategies\n- trend following\n- accumulation phases",
            "optimization_focus": "Focus on Bitcoin's high volatility, 24/7 trading nature, and correlation with traditional markets during risk-on/off periods.",
            "risk_considerations": "Bitcoin is highly volatile and can experience rapid price movements. Use appropriate position sizing and risk management."
        }
    },
    "btc-short": {
        "asset_name": "BTC (Bitcoin)", 
        "strategy_name": "btc-short-bot", 
        "symbol": "OKX:BTCUSDT.P", 
        "target_criteria": {"total_trades_min": 25, "max_drawdown_max": 30}, 
        "time_backtest": "2019 => present", 
        "target_potential": {"total_trades_min": 20, "max_drawdown_max": 50},
        "prompt_template": {
            "context": "You are an AI agent specialized in PineScript code optimization for Bitcoin (BTC) short trading strategies.",
            "asset_description": "BTC can be short in some situations like:\n- mean reversion\n- trend reversal\n- overbought conditions\n- distribution phases",
            "optimization_focus": "Focus on Bitcoin's high volatility and tendency for sharp corrections after rallies. Look for overbought signals and trend exhaustion.",
            "risk_considerations": "Shorting Bitcoin carries high risk due to its potential for rapid upward moves. Use strict stop-losses and position sizing."
        }
    },
    "eth-long": {
        "asset_name": "ETH (Ethereum)", 
        "strategy_name": "eth-long-bot", 
        "symbol": "OKX:ETHUSDT.P", 
        "target_criteria": {"total_trades_min": 25, "max_drawdown_max": 30}, 
        "time_backtest": "2019 => present", 
        "target_potential": {"total_trades_min": 20, "max_drawdown_max": 50},
        "prompt_template": {
            "context": "You are an AI agent specialized in PineScript code optimization for Ethereum (ETH) long trading strategies.",
            "asset_description": "ETH can be long in some situations like:\n- DeFi ecosystem growth\n- smart contract adoption\n- layer 2 scaling solutions\n- institutional adoption",
            "optimization_focus": "Focus on Ethereum's correlation with Bitcoin, DeFi TVL metrics, and network upgrade impacts on price action.",
            "risk_considerations": "Ethereum is highly correlated with Bitcoin but can have unique movements based on network upgrades and DeFi activity."
        }
    },
}

STRATEGY_SETTINGS = LIST_STRATEGY_SETTINGS["eth-long"]

STRATEGY_NAME = STRATEGY_SETTINGS["strategy_name"]
SYMBOL = STRATEGY_SETTINGS["symbol"]
CHART_URL = "https://www.tradingview.com/chart/LZ4CKUpi/"
_TOTAL_CONDITIONS = []
for i in range(1, 29):
    _TOTAL_CONDITIONS.append(str(i))
TOTAL_CONDITIONS = []

# Optimization Settings
TARGET_CRITERIA = STRATEGY_SETTINGS["target_criteria"]
TARGET_POTENTIAL = STRATEGY_SETTINGS["target_potential"]
ASSET_NAME = STRATEGY_SETTINGS["asset_name"]
TIME_BACKTEST = STRATEGY_SETTINGS["time_backtest"]
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
MAX_ITERATIONS = 50
MAX_CONSECUTIVE_ERRORS = 5
MAX_DUPLICATE_CONSECUTIVE_ERRORS = 5
PROCESS_COUNT = 10

# File Paths
SHEETS_DIRECTORY = "data/sheets"
REPORTS_DIRECTORY = "data/reports"
CACHE_DIRECTORY = "data/cache"
# Label Conditions
OVERFIT_CONDITIONS = {
    "TOTAL_TRADES_LOWER": 15,
    "WIN_RATE_UPPER": 80,
}

RISK_CONDITIONS = {
    "MDD_LOWER": -35,
}

GOOD_CONDITIONS = {
    "TOTAL_TRADES_UPPER": 30,
    "WIN_RATE_UPPER": 80,
}
