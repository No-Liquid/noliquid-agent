import json
import os
import sys
from file_utils import get_sheets_directory_path, find_target_workbook_file, get_workbook_file_path
from excel_reader import read_worksheet_as_json
from export_report_true import export_report
from utils import encode_signals
from config import configs

def global_test_strategy_report(filename: str): 
    target_filename = filename if len(filename) > 1 else "btc-short.xlsx"
    sheets_directory_path = get_sheets_directory_path("./sheets")
    workbook_file_path = get_workbook_file_path(
        sheets_directory_path, target_filename)
    orders = read_worksheet_as_json(workbook_file_path, 3)
    strategyReport: dict[str, any] = {}
    positions: dict[str, dict[str, any]] = {}
    conditions: dict[str, dict[str, any]] = {}
    for i, _ in enumerate(orders):
        key = "Position " + orders[i]["Date/Time"]
        if "Exit" in orders[i]["Type"]:
            if positions.get(key) is None:
                positions[key] = {
                    "orders": [],
                    "Position max drawdown %": 0.0
                }
            entryOrder = orders[min(i + 1, len(orders))]
            exitOrder = orders[i]
            positions[key]["orders"] += [entryOrder]
            entryOrderSignal = encode_signals(entryOrder["Signal"])
            orderSizePercent = entryOrderSignal["sizeEquity"]
            orderMdd = float(entryOrder["Drawdown %"])
            positions[key]["Position max drawdown %"] = 0 if exitOrder["Signal"] == "Open" else -float(exitOrder["Signal"])*100

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
                    conditions[k]["Entry Trigger Max drawdown %"] = min(conditions[k]["Entry Trigger Max drawdown %"], pos["Position max drawdown %"])
                    
                else:
                    conditions[k]["DCA Triggers time"] += 1
                    conditions[k]["DCA Trigger Max drawdown %"] = min(conditions[k]["DCA Trigger Max drawdown %"], pos["Position max drawdown %"])

                conditions[k]["Triggers time"] += 1
                conditions[k]["Max drawdown %"] = min(conditions[k]["Max drawdown %"], pos["Position max drawdown %"])
                if o["Net P&L USD"] > 0:
                    conditions[k]["Win orders"] += 1
                else:
                    conditions[k]["Lose orders"] += 1
                conditions[k]["Win rate (%)"] = conditions[k]["Win orders"] / (conditions[k]["Win orders"] + conditions[k]["Lose orders"]) * 100
    strategyReport = {
        "positions": positions,
        "totalPositions": len(positions),
        "conditions": conditions,
    }
    return strategyReport

def single_test_strategy_report(filename: str):
    target_filename = filename if len(filename) > 1 else "btc-long.xlsx"
    sheets_directory_path = get_sheets_directory_path("./sheets")
    workbook_file_path = get_workbook_file_path(
        sheets_directory_path, target_filename)
    orders = read_worksheet_as_json(workbook_file_path, 3)
    strategyReport: dict[str, any] = {}
    positions: dict[str, dict[str, any]] = {}
    conditions: dict[str, dict[str, any]] = {}
    for i, _ in enumerate(orders):
        key = "Position " + orders[i]["Date/Time"]
        if "Exit" in orders[i]["Type"]:
            if positions.get(key) is None:
                positions[key] = {
                    "orders": [],
                    "Position max drawdown %": 0.0
                }
            entryOrder = orders[min(i + 1, len(orders))]
            exitOrder = orders[i]
            positions[key]["orders"] += [entryOrder]
            entryOrderSignal = encode_signals(entryOrder["Signal"])
            orderSizePercent = entryOrderSignal["sizeEquity"]
            orderMdd = float(entryOrder["Drawdown %"])
            positions[key]["Position max drawdown %"] = 0 if exitOrder["Signal"] == "Open" else -float(exitOrder["Signal"])*100

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
                    conditions[k]["Entry Trigger Max drawdown %"] = min(conditions[k]["Entry Trigger Max drawdown %"], pos["Position max drawdown %"])
                    
                else:
                    conditions[k]["DCA Triggers time"] += 1
                    conditions[k]["DCA Trigger Max drawdown %"] = min(conditions[k]["DCA Trigger Max drawdown %"], pos["Position max drawdown %"])

                conditions[k]["Triggers time"] += 1
                conditions[k]["Max drawdown %"] = min(conditions[k]["Max drawdown %"], pos["Position max drawdown %"])
                if o["Net P&L USD"] > 0:
                    conditions[k]["Win orders"] += 1
                else:
                    conditions[k]["Lose orders"] += 1
                conditions[k]["Win rate (%)"] = conditions[k]["Win orders"] / (conditions[k]["Win orders"] + conditions[k]["Lose orders"]) * 100
    strategyReport = {
        "positions": positions,
        "totalPositions": len(positions),
        "conditions": conditions,
    }
    return strategyReport
