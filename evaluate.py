import sys
from pathlib import Path
import asyncio
import playwright

from train.embedding import load_pine_code
sys.path.insert(0, str(Path(__file__).parent / "src"))

from automation.tradingview_bot import TradingViewBot
from utils.config_manager import ConfigManager
from utils.report_exporter import ReportExporter
from analytics.strategy_analyzer import StrategyAnalyzer
from playwright.async_api import async_playwright
import json
import os
async def main(_config:any):
    config = _config
    strategy_settings = config['STRATEGY_SETTINGS']
    if not config["TOTAL_CONDITIONS"]:
        cache_dir = Path(config['CACHE_DIRECTORY'])
        if cache_dir.exists():
            exporter = ReportExporter()
            path = os.path.join(config['CACHE_DIRECTORY'], f"{strategy_settings['strategy_name']}.json")
            cached_data = exporter.load_cache(path)
            exporter.exports(cached_data, strategy_settings['strategy_name'])
    else:
        async with async_playwright() as playwright:
            user_agent = config["USER_AGENT"]
            browser_context = await playwright.chromium.launch_persistent_context(
                "./chrome_data_analytics",
                headless=False,
                slow_mo=1000,
                user_agent=user_agent,
            )
            page = await browser_context.new_page()

            tdv = TradingViewBot(config)
            await tdv.action_setup_tradingview_login(page)
            await tdv.action_goto_supercharts(page)
            await tdv.action_handle_optional_dialogs(page)
            await tdv.action_setup_strategy(page)
            # strategy_code = load_pine_code(path="train/dev.pine")
            # await tdv.action_override_code(page, strategy_code)
            await tdv.action_add_or_update_script(page)
            await tdv.action_analytics_strategy_global_test(page)
            await tdv.action_analytics_strategy_single_test(page)

# asyncio.run(main())
# 