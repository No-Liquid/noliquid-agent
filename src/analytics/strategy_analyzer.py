"""
Strategy analysis and performance calculation module.
"""

import os
from typing import Dict, Any, List
from utils.excel_reader import ExcelReader
from utils.signal_processing import encode_signals
from utils.file_operations import get_data_directory, get_file_path
import json
class StrategyAnalyzer:
    """Analyzes trading strategy performance from Excel data."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.excel_reader = ExcelReader()
    
    def analyze_file(self, filename: str) -> Dict[str, Any]:
        """
        Analyze strategy performance (global test version).
        
        Args:
            filename: Name of Excel file to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        target_filename = filename if len(filename) > 1 else "btc-long.xlsx"
        sheets_dir = get_data_directory("sheets")
        file_path = get_file_path(sheets_dir, target_filename)
        orders = self.excel_reader.read_worksheet_as_json(file_path, 3)
        summary = self.excel_reader.read_worksheet_as_json(file_path, 0)
        perform = self.excel_reader.read_worksheet_as_json(file_path, 1)
        ratio = self.excel_reader.read_worksheet_as_json(file_path, 2)

        # print(json.dumps(perform1, indent=4))
        strategy_report: Dict[str, Any] = {}
        positions: Dict[str, Dict[str, Any]] = {}
        conditions: Dict[str, Dict[str, Any]] = {}
        
        for i, order in enumerate(orders):
            if order.get("Date/Time", "") == "":
                continue
            key = "Position " + order.get("Date/Time", "")
            if "Exit" in order["Type"]:
                if positions.get(key) is None:
                    positions[key] = {
                        "orders": [],
                        "Position max drawdown %": 0.0
                    }
                entry_order = orders[min(i + 1, len(orders) - 1)]
                exit_order = order
                positions[key]["orders"] += [entry_order]
                entry_order_signal = encode_signals(entry_order["Signal"])
                order_size_percent = entry_order_signal["sizeEquity"]
                order_mdd = float(entry_order["Drawdown %"])
                positions[key]["Position max drawdown %"] = (
                    0 if exit_order["Signal"] == "Open" 
                    else -float(exit_order["Signal"]) * 100
                )

        for p in positions:
            pos = positions[p]
            for i, o in enumerate(pos["orders"]):
                keys = str(o["Signal"]).split(" | ")[0]
                for k in keys.split(" ")[:-1]:
                    if conditions.get(k) is None:
                        conditions[k] = {
                            "Entry Triggers time": 0,
                            "DCA Triggers time": 0,
                            "Triggers time": 0,
                            "Max drawdown %": pos["Position max drawdown %"],
                            "Entry Trigger Max drawdown %": pos["Position max drawdown %"],
                            "DCA Trigger Max drawdown %": pos["Position max drawdown %"],
                            "Win orders": 0,
                            "Lose orders": 0,
                            "Win rate (%)": 0,
                            "P&L USD": 0,
                            "P&L (%)": 0
                        }
                    if i == 0:
                        conditions[k]["Entry Triggers time"] += 1
                        conditions[k]["Entry Trigger Max drawdown %"] = min(
                            conditions[k]["Entry Trigger Max drawdown %"], 
                            pos["Position max drawdown %"]
                        )
                    else:
                        conditions[k]["DCA Triggers time"] += 1
                        conditions[k]["DCA Trigger Max drawdown %"] = min(
                            conditions[k]["DCA Trigger Max drawdown %"], 
                            pos["Position max drawdown %"]
                        )

                    conditions[k]["Triggers time"] += 1
                    conditions[k]["Max drawdown %"] = min(
                        conditions[k]["Max drawdown %"], 
                        pos["Position max drawdown %"]
                    )
                    if o["Net P&L USD"] > 0:
                        conditions[k]["Win orders"] += 1
                    else:
                        conditions[k]["Lose orders"] += 1
                    conditions[k]["Win rate (%)"] = (
                        conditions[k]["Win orders"] / 
                        (conditions[k]["Win orders"] + conditions[k]["Lose orders"]) * 100
                    )
        
        # Tag conditions based on config thresholds
        
        strategy_report = {
            "orders": orders,
            "positions": positions,
            "Total positions": len(positions),
            "conditions": conditions,
            "Net profit %": summary[1].get("All %", ""),
            "Max drawdown %": min(positions.values(), key=lambda x: x["Position max drawdown %"])["Position max drawdown %"] if positions else 0.0
        }
        analytic = perform + ratio + summary
        for data in analytic:
            key = data.get("Unnamed: 0", "")
            if key:  # Only add if key is not empty
                usd_value = data.get("All USD", "")
                pct_value = data.get("All %", "")
                strategy_report[key] = usd_value if str(usd_value) != "nan" else pct_value
        strategy_report = self._tag_conditions(strategy_report)
        return strategy_report
    
    def _tag_conditions(self, strategy_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tag conditions based on config thresholds.
        
        Args:
            conditions: Conditions dictionary
            
        Returns:
            Conditions dictionary with tags added
        """
        overfit_conditions = self.config.get("OVERFIT_CONDITIONS", {})
        risk_conditions = self.config.get("RISK_CONDITIONS", {})
        good_conditions = self.config.get("GOOD_CONDITIONS", {})
        
        # for condition_key, condition_data in conditions.items():
        tags = []
        total_trades = strategy_report.get("Total trades", 0)
        win_rate = strategy_report.get("Percent profitable", 0)
        max_dd = strategy_report.get("Max drawdown %", 0)
        # Check OVERFIT conditions
        if "TOTAL_TRADES_LOWER" in overfit_conditions and "WIN_RATE_UPPER" in overfit_conditions:
            if total_trades < overfit_conditions["TOTAL_TRADES_LOWER"] and win_rate > overfit_conditions["WIN_RATE_UPPER"]:
                tags.append("OVERFIT")
                # return strategy_report

        # Check RISK conditions
        if "MDD_LOWER" in risk_conditions:
            if max_dd < risk_conditions["MDD_LOWER"]:
                tags.append("RISK")
                # return strategy_report
        
        if "TOTAL_TRADES_UPPER" in good_conditions and "WIN_RATE_UPPER" in good_conditions:
            if total_trades > good_conditions["TOTAL_TRADES_UPPER"] and win_rate > good_conditions["WIN_RATE_UPPER"]:
                tags.append("GOOD")

        if len(tags) == 0:
            tags.append("NORMAL")
        strategy_report["tags"] = tags
        
        return strategy_report