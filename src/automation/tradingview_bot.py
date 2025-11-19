"""
TradingView automation bot for downloading strategy reports (Async Version).
"""
import asyncio
import pyotp
from playwright.async_api import async_playwright
import re
from typing import Dict, Any
from analytics.strategy_analyzer import StrategyAnalyzer
import json
import os
from pathlib import Path

from src.utils.report_exporter import ReportExporter

class TradingViewBot:
    """Automated TradingView strategy report downloader."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TradingView bot.

        Args:
            config: Configuration dictionary containing credentials and settings
        """
        self.config = config
        self.username = config.get("TRADINGVIEW_USER", config.get("_user", ""))
        self.password = config.get("TRADINGVIEW_PASS", config.get("_pass", ""))
        self.secret_2fa = config.get(
            "TRADINGVIEW_2FA_SECRET", config.get("_2fa_secret", ""))
        self.strategy_name = config.get("STRATEGY_NAME", "btc-long")
        self.total_conditions = config.get("TOTAL_CONDITIONS", ["1", "2", "3"])
        self.chart_url = config.get(
            "CHART_URL", "https://www.tradingview.com/chart/bQN4MJLY/")
        self.symbol = config.get("SYMBOL", "OKX:BTCUSDT.P")

        # Validate that total_conditions is a list
        if not isinstance(self.total_conditions, list):
            #print(
                # f"⚠️ Warning: TOTAL_CONDITIONS should be a list, got {type(self.total_conditions)}. Converting to list.")
            if isinstance(self.total_conditions, int):
                self.total_conditions = [
                    str(i) for i in range(1, self.total_conditions + 1)]
            else:
                self.total_conditions = [str(self.total_conditions)]

        #print(f"📋 Processing conditions: {self.total_conditions}")
        self.reports: dict[str, Any] = {}
        self.reports['global_test'] = {}
        self.reports['single_test'] = {}

    async def action_setup_tradingview_login(self, page):
        """Handle TradingView login process and land on Supercharts."""
        #print("[INFO] Navigating to TradingView...")
        await page.goto("https://www.tradingview.com/accounts/signin/")
        await asyncio.sleep(2)

        try:
            email_btn_visible = await page.get_by_role("button", name="Email").is_visible(timeout=5000)
            signin_btn_visible = await page.get_by_role("button", name="Sign in").is_visible(timeout=5000)

            if email_btn_visible or signin_btn_visible:
                #print("[INFO] Logging in...")
                try:
                    await page.get_by_role("button", name="Email").click(timeout=5000)
                except:
                    pass

                await page.get_by_role("textbox", name="Email or Username").click(timeout=5000)
                await page.get_by_role("textbox", name="Email or Username").fill(self.username)
                await page.get_by_role("textbox", name="Password").click(timeout=5000)
                await page.get_by_role("textbox", name="Password").fill(self.password)
                await page.get_by_role("button", name="Sign in").click(timeout=5000)

                # Handle 2FA if enabled
                if self.secret_2fa:
                    #print("[INFO] Generating 2FA code...")
                    totp = pyotp.TOTP(self.secret_2fa)
                    code = totp.now()
                    await page.get_by_role(
                        "textbox", name="Code from your app or backup").fill(code)
            else:
                pass
                # await page.screenshot(path='tradingview-login.png')
                #print("[INFO] Already logged in")
        except Exception as e:
            #print(f"[WARNING] Could not login: {e}")
            pass

    async def action_goto_supercharts(self, page):
        await page.goto(f"{self.chart_url}?symbol={self.symbol}", wait_until="commit")

    async def action_handle_optional_dialogs(self, page):
        """Handle optional dialogs that may appear."""
        dialogs_to_try = [
            "Decline offer",
            "Decline",
            "No thanks",
            "Dismiss",
            "Close"
        ]

        for dialog_text in dialogs_to_try:
            try:
                if await page.get_by_role("button", name=dialog_text).is_visible(timeout=5000):
                    await page.get_by_role("button", name=dialog_text).click(timeout=5000)
                    #print(f"[INFO] Closed dialog: {dialog_text}")
                    break
            except:
                continue

    async def action_setup_strategy(self, page):
        """Setup Pine Editor and load strategy."""
        # Open Pine Editor
        #print("[INFO] Waiting for page to load...")
        await asyncio.sleep(2)

        try:
            await page.get_by_role("progressbar").wait_for(state="hidden", timeout=30000)
        except:
            pass
        

        try:
            await page.get_by_role("button", name="Publish indicator").wait_for(state="visible", timeout=60000)
        except:
            await asyncio.sleep(10)
            pass

        try:
            await page.get_by_role(
                "button", name="Open Pine Editor").click(timeout=3000)
        except:
            await self.action_handle_optional_dialogs(page)
            pass

        #print("[INFO] Loading strategy script...")

        try:
            await page.locator(".view-lines > div:nth-child(3)").click(timeout=5000)
            await page.get_by_role(
                "textbox", name="Editor content;Press Alt+F1").press("ControlOrMeta+o")
        except:
            await self.action_handle_optional_dialogs(page)
            await page.locator(".view-lines > div:nth-child(3)").click(timeout=5000)
            await page.get_by_role(
                "textbox", name="Editor content;Press Alt+F1").press("ControlOrMeta+o")
            pass

        await page.get_by_role("searchbox", name="Search").fill(self.strategy_name)

        try:
            #print(f"[INFO] Selected strategy: {self.strategy_name}")
            await page.locator("div").filter(has_text=re.compile(
                rf"^{self.strategy_name}$")).nth(1).click(timeout=5000)

            if await page.locator("span").filter(has_text=re.compile(r"^Yes$")).nth(1).is_visible(timeout=5000):
                await page.locator("span").filter(has_text=re.compile(r"^Yes$")).nth(1).click(timeout=5000)
        except:
            await page.locator("div").filter(has_text=re.compile(
                rf"^{self.strategy_name}$")).nth(2).click(timeout=5000)
            pass

        try:
            await page.get_by_role("button", name="Close menu").click(timeout=5000)
        except:
            pass

    async def action_override_code(self, page, code: str):
        try:
            await page.get_by_text("restore this version").first.click(timeout=3000)
        except Exception as e:
            pass

        try:
            await page.locator("#pine-editor-bottom").get_by_role("button").first.click(timeout=500)
        except:
            pass

        try:
            await page.get_by_role("button", name="Open Pine Editor").click(timeout=500)
        except:
            pass

        await page.locator(".view-lines > div:nth-child(3)").click(timeout=5000)
        await page.get_by_role("textbox", name="Editor content;Press Alt+F1").press("ControlOrMeta+a")
        await page.get_by_role("textbox", name="Editor content;Press Alt+F1").fill("\n\n\n")
        await page.get_by_role("textbox", name="Editor content;Press Alt+F1").fill(code)

    async def action_add_or_update_script(self, page):
        try:
            await page.locator("div").filter(has_text=re.compile(r"^Add to chartSave$")).nth(2).dblclick(timeout=500)
            await page.click('[data-qa-id="yes-btn"]', timeout=1000)
            await page.locator("div").filter(has_text=re.compile(r"^Add to chartSave$")).nth(2).dblclick(timeout=500)
            await page.click('[data-qa-id="yes-btn"]', timeout=1000)
        except:
            pass

        try:
            await page.locator("#pine-editor-bottom").get_by_text("Update on chart").click(timeout=500)
        except:
            pass

        try:
            await page.get_by_role(
                "button", name="Open Strategy Tester").click(timeout=500)
        except:
            pass
    async def action_analytics_strategy_global_test(self, page):
        self.reports["global_test"] = {}

        await self.action_set_single_test_condition(page, '')
        await self.action_set_date_range_entire(page)
        await self.action_wait_for_backtest(page)
        filename = await self.action_download_report(page, self.strategy_name)

        analyzer = StrategyAnalyzer(self.config)
        exporter = ReportExporter()
        g_results = analyzer.analyze_file(filename)
        self.reports["global_test"] = g_results
        exporter.exports(self.reports, filename)

    async def action_analytics_strategy_single_test(self, page, override_name: any = None):
        self.reports["single_test"] = {}

        for condition_num in self.total_conditions:
            try:
                await page.get_by_role("button", name="Open Strategy Tester").click(timeout=3000)
            except:
                pass

            await asyncio.sleep(5)
            await self.action_set_single_test_condition(page, condition_num)
            await self.action_set_date_range_entire(page)
            await self.action_wait_for_backtest(page)

            filename = await self.action_download_report(page, override_name if override_name else f"{self.strategy_name}")

            analyzer = StrategyAnalyzer(self.config)
            s_results = analyzer.analyze_file(filename)
            exporter = ReportExporter()
            # Check if condition data is empty/empty string
            if not s_results or s_results == "":
                #print(
                    # f"⚠️ Condition {condition_num}: Data is empty, will use global test data")
                self.reports["single_test"][condition_num] = ""
            else:
                self.reports["single_test"][condition_num] = s_results
                #print(
                    # f"✅ Condition {condition_num}: Data collected successfully")

            # Export cache after each condition is completed
            #print(f"💾 Exporting cache after condition {condition_num}...")
            exporter.exports(self.reports, filename)

        return self.reports
    async def action_set_single_test_condition(self, page, condition: str):
        """Set single test condition."""
        #print(f"[INFO] Setting test condition: '{condition}'")

        try:
            await page.get_by_role("button", name=f"{self.strategy_name} report").click(timeout=5000)
        except:
            try:
                await page.get_by_role("button", name="Open Strategy Tester").click(timeout=5000)
            except:
                await page.get_by_role("button", name="Open Pine Editor").click(timeout=5000)
                await self.action_add_or_update_script(page)
                pass
            await page.get_by_role("button", name=f"{self.strategy_name} report").click(timeout=5000)
            pass

        try:
            await page.get_by_text("Settings…").click(timeout=5000)
        except Exception as e:
            await page.locator("body").press("ControlOrMeta+p")
        try:
            await page.get_by_role("tab", name="Inputs").click(timeout=5000)
        except:
            pass

        textbox = page.locator("span").filter(
            has_text="Single Test Condition").get_by_role("textbox")
        await textbox.click(timeout=3000)
        await textbox.fill(condition)
        await page.get_by_role("button", name="Ok").click(timeout=5000)

    async def action_set_date_range_entire(self, page):
        """Set date range to entire history."""
        try:
            await page.click("div.dateRangeMenuWrapper-ucbE4pMM", timeout=5000)
            await page.get_by_text("Entire history").click(timeout=5000)
        except:
            print("[WARNING] Could not set date range to entire history")

    async def action_wait_for_backtest(self, page):
        """Wait for backtest to complete."""
        #print("[INFO] Waiting for backtest to complete...")

        async def wait(page):
            loading1 = page.locator('#bottom-area').get_by_role('progressbar')
            loading2 = page.get_by_text("Updating report")
            loading3 = page.locator("#snackbar-container span").first

            try:
                if await loading1.is_visible(timeout=5000):
                    await loading1.wait_for(state="hidden", timeout=100000)
                    #print("[INFO] Loading1 hidden")

                if await loading2.is_visible(timeout=5000):
                    await loading2.wait_for(state="hidden", timeout=100000)
                    #print("[INFO] Loading2 hidden")

                if await loading3.is_visible(timeout=5000):
                    await loading3.wait_for(state="hidden", timeout=100000)
                    #print("[INFO] Loading3 hidden")
            except Exception as e:
                #print(f"[WARNING] Could not wait for backtest to complete: {e}")
                pass

        try:
            await wait(page)
        except Exception as e:
            #print(f"[WARNING] Could not wait for backtest to complete: {e}")
            await self.action_set_date_range_entire(page)
            await wait(page)

    async def action_download_report(self, page, report_name: str):
        """Download strategy report."""
        #print(f"[INFO] Downloading {report_name} report...")

        try:
            await page.get_by_role("button", name="Open Strategy Tester").click(timeout=1000)
        except:
            pass

        await page.get_by_role("button", name=f"{self.strategy_name} report").click(timeout=5000)

        async with page.expect_download() as download_info:
            await page.get_by_text("Download data as XLSX").click(timeout=5000)

        download = await download_info.value
        filename = f"{report_name}.xlsx"

        # Save to data/sheets directory
        from utils.file_operations import get_data_directory, ensure_directory
        sheets_dir = get_data_directory("sheets")
        ensure_directory(sheets_dir)
        save_path = os.path.join(sheets_dir, filename)

        await download.save_as(save_path)
        #print(f"[INFO] Saved as {filename}")

        await asyncio.sleep(1)
        return filename