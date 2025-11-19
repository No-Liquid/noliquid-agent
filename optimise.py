"""
Trading Analytics Tool - Main Entry Point (Async Version)
"""

import sys
from pathlib import Path
from src.utils.clipboard_utils import copy_strategy_code_to_clipboard, copy_to_clipboard
from src.utils.lmm_utils import decode_LMM_output, add_to_cache

sys.path.insert(0, str(Path(__file__).parent / "src"))

from automation.tradingview_bot import TradingViewBot
from utils.config_manager import ConfigManager
from utils.report_exporter import ReportExporter
from analytics.strategy_analyzer import StrategyAnalyzer
import asyncio
import pyotp
from playwright.async_api import async_playwright
import re
from typing import Dict, Any
import json
import os
from pathlib import Path
from train.embedding import run_strategy_embedding, load_pine_code
from utils.github_utils import auto_commit_and_push
from utils.process_logger import init_logger
import shutil


def main():
    """Main application entry point - runs TradingView automation or exports from cache."""
    config_manager = ConfigManager("config.py")
    config = config_manager.get_config()
    asyncio.run(run_strategy_agent(config))


def is_target_criteria(results, target):
    """Check if backtest results meet target criteria"""
    return (results["Total trades"] >= target["total_trades_min"] and 
            abs(results["Max drawdown %"]) <= target["max_drawdown_max"])


async def run_strategy_agent(config):
    """Run TradingView automation to download and analyze fresh data with async parallel execution."""
    
    # Initialize logger
    logger = init_logger()
    
    async with async_playwright() as playwright:
        user_agent = config["USER_AGENT"]
        
        # Launch browser
        browser_context = await playwright.chromium.launch_persistent_context(
            "./chrome_data_open",
            headless=False,
            slow_mo=1000,
            user_agent=user_agent,
        )
        
        # Setup login
        print("[INFO] Check authentication")
        login_page = await browser_context.new_page()
        tdv_login = TradingViewBot(config)
        await tdv_login.action_setup_tradingview_login(login_page)
        await login_page.close()
        await asyncio.sleep(5)
        exporter = ReportExporter()
        print("[INFO] Authenticate successfully")

        async def excute_optimise(pc_name: str, pc_page: Any):
            """Execute optimization for a single strategy"""
            try:
                pinescript_path = f"train/{pc_name}.pine"
                code = load_pine_code(path = pinescript_path)
                if code == "":
                    shutil.copy("train/dev.pine", f"train/{pc_name}.pine",follow_symlinks=True)

                logger.update(pc_name, status='INIT', message='Loading cache')
                
                cache = exporter.load_cache(pc_name)
                if not cache:
                    cache = {}
                
                # Setup optimization parameters
                target = config["TARGET_CRITERIA"]
                name = config["ASSET_NAME"]
                time_backtest = config["TIME_BACKTEST"]
                target_potential = config["TARGET_POTENTIAL"]
                ensemble_open_long = config["TOTAL_CONDITIONS"][0]
                max_iterations = config["MAX_ITERATIONS"]
                max_consecutive_errors = config["MAX_CONSECUTIVE_ERRORS"]
                
                single_test_cache = cache.get("single_test", {})
                backtest = single_test_cache.get(ensemble_open_long, {})
                
                consecutive_errors = 0
                lmm_res = {}
                iteration_count = 0
                duplicate_consecutive_errors = 0 
                
                # Initialize TradingView bot with process name
                tdv = TradingViewBot(config)
                
                logger.update(pc_name, status='RUNNING', message='Setting up TradingView')
                await tdv.action_goto_supercharts(pc_page)
                logger.update(pc_name, status='RUNNING', message='Supper Chart TradingView')
                await tdv.action_handle_optional_dialogs(pc_page)
                await tdv.action_setup_strategy(pc_page)
                logger.update(pc_name, status='RUNNING', message='Setup Done TradingView')
                strategy_code = load_pine_code(path=pinescript_path)
                await tdv.action_override_code(pc_page, strategy_code)
                await tdv.action_add_or_update_script(pc_page)
                await tdv.action_analytics_strategy_single_test(pc_page, pc_name)
                
                backtest = tdv.reports["single_test"][ensemble_open_long]
                
                logger.update(
                    pc_name,
                    status='RUNNING',
                    iteration=0,
                    trades=backtest.get('Total trades', 'N/A'),
                    drawdown=backtest.get('Max drawdown %', 'N/A'),
                    net_profit=backtest.get('Net profit %', 'N/A'),
                    message='Initial backtest complete'
                )
                
                # Optimization loop
                while (not is_target_criteria(backtest, target) and
                       iteration_count < max_iterations and
                       consecutive_errors < max_consecutive_errors):
                    if duplicate_consecutive_errors >= config["MAX_DUPLICATE_CONSECUTIVE_ERRORS"]:
                        shutil.copy("train/dev.pine", f"train/{pc_name}.pine",follow_symlinks=True)
                        logger.update(pc_name, message='Duplicate consecutive errors, reset to dev.pine')
                        lmm_res = {"assistant": ""}
                    iteration_count += 1
                    logger.update(pc_name, iteration=iteration_count, message='Generating strategy')
                    
                    # Step 1: Generate new strategy code
                    lmm_res = await run_strategy_embedding(
                        name=name,
                        time_backtest=time_backtest,
                        condition_id=ensemble_open_long,
                        net_profit_percent=backtest["Net profit %"],
                        max_drawdown_percent=backtest["Max drawdown %"],
                        total_trades=backtest["Total trades"],
                        percent_profitable=backtest["Percent profitable"],
                        target=target,
                        tool=config['TOOL'],
                        assitent_comment_before=lmm_res.get("assistant", ""),
                        command="agent",
                        model="auto",
                        pinescript_path=pinescript_path
                    )
                    
                    await asyncio.sleep(2)
                    
                    # Step 2: Apply strategy to TradingView and execute backtest
                    try:
                        logger.update(pc_name, message='Applying Pine Script')
                        
                        strategy_code = load_pine_code(path=pinescript_path)
                        logger.update(pc_name, status='RUNNING', message='Override code')
                        await tdv.action_override_code(pc_page, strategy_code)
                        await tdv.action_add_or_update_script(pc_page)
                        logger.update(pc_name, message='Executing backtest')
                        await tdv.action_analytics_strategy_single_test(pc_page, pc_name)
                        
                        # Update cache with new results
                        new_backtest = tdv.reports["single_test"][ensemble_open_long]
                        if backtest["Total trades"] == new_backtest["Total trades"] and backtest["Max drawdown %"] == new_backtest["Max drawdown %"] and backtest["Net profit %"] == new_backtest["Net profit %"]:
                            duplicate_consecutive_errors += 1
                        else:
                            duplicate_consecutive_errors = 0
                        backtest = new_backtest
                        
                        logger.update(
                            pc_name,
                            iteration=iteration_count,
                            trades=backtest.get('Total trades', 'N/A'),
                            drawdown=backtest.get('Max drawdown %', 'N/A'),
                            net_profit=backtest.get('Net profit %', 'N/A'),
                            message='Backtest complete',
                            errors=consecutive_errors
                        )
                        
                        # Save results
                        option = os.environ.get("OPTION", "github")
                        file_path = "data/prompts/" + (
                            "potential_conditions.json" if is_target_criteria(backtest, target_potential) 
                            else "another_conditions.json"
                        )
                        github_message = (
                            f"{pc_name} | "
                            f"{'potential' if is_target_criteria(backtest, target_potential) else 'worse'} "
                            f"[TT|{backtest['Total trades']}] "
                            f"[MDD|{backtest['Max drawdown %']}%] "
                            f"[NP|{backtest['Net profit %']}%] "
                            f"[PP|{backtest['Percent profitable']}]"
                        )
                        
                        if option == "cache_json":
                            add_to_cache({
                                **lmm_res,
                                "max_drawdown_percent": backtest["Max drawdown %"],
                                "net_profit_percent": backtest["Net profit %"],
                                "total_trades": backtest["Total trades"],
                                "percent_profitable": 0 if backtest["Percent profitable"] == "NaN" 
                                                     else backtest["Percent profitable"],
                            }, file_path)
                        elif option == "github":
                            auto_commit_and_push(github_message, files_path=[pinescript_path, f"data/cache/{pc_name}.json", f"data/reports/{pc_name}.txt", f"data/reports/{pc_name}.xlsx", f"data/sheets/{pc_name}.xlsx"])
                        consecutive_errors = 0
                        
                    except Exception as e:
                        try:
                            await tdv.action_handle_optional_dialogs(pc_page)
                        except:
                            pass
                        
                        consecutive_errors += 1
                        logger.update(
                            pc_name,
                            errors=consecutive_errors,
                            message=f'Error: {str(e)[:30]}'
                        )
                        continue
                    
                    await asyncio.sleep(1)
                
                # Final status update
                if iteration_count >= max_iterations:
                    logger.update(
                        pc_name, 
                        status='DONE', 
                        message=f'Max iterations reached: {max_iterations}'
                    )
                elif consecutive_errors >= max_consecutive_errors:
                    logger.update(
                        pc_name, 
                        status='ERROR', 
                        message=f'Too many errors: {consecutive_errors}'
                    )
                else:
                    logger.update(
                        pc_name, 
                        status='DONE', 
                        message='Target criteria met'
                    )
                    
            except Exception as e:
                logger.update(pc_name, status='ERROR', message=f'Fatal: {str(e)[:30]}')
                raise e
        
        # Run all optimizations in parallel with live table display
        pages = [await browser_context.new_page() for _ in range(config["PROCESS_COUNT"])]
        
        # Start live display
        await logger.start_live_display()
        
        # Run optimization tasks
        optimization_tasks = [
            excute_optimise(f"pc_{i}", pages[i]) 
            for i in range(len(pages))
        ]
        
        # Wait for all optimizations to complete
        await asyncio.gather(*optimization_tasks, return_exceptions=True)
        
        # Stop display
        await logger.stop_live_display()
        
        await asyncio.sleep(5)
        await browser_context.close()


# if __name__ == "__main__":
#     main()
