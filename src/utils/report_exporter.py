"""
Report export utilities for trading analytics.
"""

import os
import re
from typing import Dict, Any, List, Tuple
import pandas as pd
from .file_operations import get_data_directory, ensure_directory
from .signal_processing import encode_signals

import json
class ReportExporter:
    """Exports trading analysis results to formatted reports."""
    
    def save_cache(self, strategy_report: Dict[str, Any], file_name: str):
        """Save report to JSON cache file."""
        try:
            cache_dir = get_data_directory("cache")
            ensure_directory(cache_dir)
            
            strategy_name = os.path.splitext(file_name)[0]
            cache_file = os.path.join(cache_dir, f"{strategy_name}.json")
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(strategy_report, f, indent=2)
            
            print(f"💾 Cached to: {cache_file}")
        except Exception as e:
            print(f"❌ Cache save failed: {e}")
    
    def load_cache(self, file_path: str) -> Dict[str, Any]:
        """Load report from JSON cache file."""
        try:
            cache_file = os.path.join(file_path)
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Cache load failed: {e}")
        
        return None
    
    def export_txt(self, strategy_report: Dict[str, Any], file_name: str) -> Tuple[bool, str]:
        """
        Export analysis results to text report.
        
        Args:
            strategy_report: Analysis results dictionary
            file_name: Source Excel filename
            
        Returns:
            Tuple of (success, output_path or error_message)
        """
        try:
            # Prepare output directory and filename
            reports_dir = get_data_directory("reports")
            ensure_directory(reports_dir)
            
            output_filename = os.path.splitext(file_name)[0] + ".txt"
            output_path = os.path.join(reports_dir, output_filename)
            # Handle both single report and multi-test report structures
            if "global_test" in strategy_report and "single_test" in strategy_report:
                # Multi-test structure
                global_data = strategy_report["global_test"]
                single_data = strategy_report["single_test"]
                positions = global_data.get("positions", {}) or {}
                conditions = global_data.get("conditions", {}) or {}
                total_positions = global_data.get("totalPositions", len(positions))
            else:
                # Single report structure
                positions = strategy_report.get("positions", {}) or {}
                conditions = strategy_report.get("conditions", {}) or {}
                total_positions = strategy_report.get("totalPositions", len(positions))
                single_data = None

            lines: List[str] = []

            # Header
            title = "Strategy Report"
            lines.append(title)
            lines.append("=" * len(title))
            lines.append("")
            lines.append(f"Source sheet: {file_name}")
            lines.append(f"Total positions: {total_positions}")
            lines.append("")

            # Single Test section (if available)
            if single_data and isinstance(single_data, dict):
                lines.append("Single Test Performance")
                lines.append("-" * len("Single Test Performance"))
                
                # Extract condition data from single_test
                single_test_conditions = []
                for condition_key, condition_data in single_data.items():
                    # Skip empty condition names
                    if not condition_key or str(condition_key).strip() == "":
                        continue
                        
                    if isinstance(condition_data, dict):
                        # Extract performance metrics
                        total_trades = condition_data.get("Total trades", 0)
                        max_drawdown = condition_data.get("Max drawdown %", 0)
                        profit_factor = condition_data.get("Profit factor", 0)
                        win_rate = condition_data.get("Percent profitable", 0)
                        net_profit_pct = condition_data.get("Net profit %", 0)
                        sharpe_ratio = condition_data.get("Sharpe ratio", 0)
                        sortino_ratio = condition_data.get("Sortino ratio", 0)
                        
                        # Get tags from strategy report level (for single test conditions)
                        tags = condition_data.get("tags", [])
                        # print(f"DEBUG: Tags for condition {condition_key}: {tags} (type: {type(tags)})")
                        
                        single_test_conditions.append({
                            "condition": condition_key,
                            "total_trades": total_trades,
                            "max_drawdown": max_drawdown,
                            "profit_factor": profit_factor,
                            "win_rate": win_rate,
                            "net_profit_pct": net_profit_pct,
                            "sharpe_ratio": sharpe_ratio,
                            "sortino_ratio": sortino_ratio,
                            "tags": tags
                        })
                
                if single_test_conditions:
                    # Sort conditions numerically if possible
                    def _single_test_sort_key(item):
                        condition = str(item["condition"]).strip()
                        if condition.isdigit():
                            return (0, int(condition))
                        return (1, condition)
                    
                    single_test_conditions.sort(key=_single_test_sort_key)
                    
                    # Calculate column widths
                    cond_w = max(len("Condition"), max(len(str(item["condition"])) for item in single_test_conditions))
                    trades_w = max(len("Total Trades"), max(len(str(int(item["total_trades"]))) for item in single_test_conditions))
                    drawdown_w = max(len("Max Drawdown %"), max(len(self._format_drawdown_percent(item["max_drawdown"])) for item in single_test_conditions))
                    profit_w = max(len("Profit Factor"), max(len(self._format_number(item["profit_factor"])) for item in single_test_conditions))
                    winrate_w = max(len("Win Rate %"), max(len(self._format_percent(item["win_rate"])) for item in single_test_conditions))
                    netprofit_w = max(len("Net Profit %"), max(len(self._format_percent(item["net_profit_pct"])) for item in single_test_conditions))
                    sharpe_w = max(len("Sharpe Ratio"), max(len(self._format_number(item["sharpe_ratio"])) for item in single_test_conditions))
                    sortino_w = max(len("Sortino Ratio"), max(len(self._format_number(item["sortino_ratio"])) for item in single_test_conditions))
                    tags_w = max(len("Tags"), max(len(', '.join(item["tags"]) if item["tags"] else '') for item in single_test_conditions))
                    
                    # Create header
                    header = (
                        f"{'Condition'.ljust(cond_w)}  "
                        f"{'Total Trades'.rjust(trades_w)}  "
                        f"{'Max Drawdown %'.rjust(drawdown_w)}  "
                        f"{'Profit Factor'.rjust(profit_w)}  "
                        f"{'Win Rate %'.rjust(winrate_w)}  "
                        f"{'Net Profit %'.rjust(netprofit_w)}  "
                        f"{'Sharpe Ratio'.rjust(sharpe_w)}  "
                        f"{'Sortino Ratio'.rjust(sortino_w)}  "
                        f"{'Tags'.ljust(tags_w)}"
                    )
                    sep = (
                        f"{'-' * cond_w}  "
                        f"{'-' * trades_w}  "
                        f"{'-' * drawdown_w}  "
                        f"{'-' * profit_w}  "
                        f"{'-' * winrate_w}  "
                        f"{'-' * netprofit_w}  "
                        f"{'-' * sharpe_w}  "
                        f"{'-' * sortino_w}  "
                        f"{'-' * tags_w}"
                    )
                    
                    lines.append(header)
                    lines.append(sep)
                    
                    # Add data rows and calculate summary metrics
                    total_trades_sum = 0
                    max_drawdown_values = []
                    profit_factor_values = []
                    win_rate_values = []
                    net_profit_values = []
                    sharpe_ratio_values = []
                    sortino_ratio_values = []
                    
                    for item in single_test_conditions:
                        tag_display = ', '.join(item['tags']) if item['tags'] else ''
                        # print(f"DEBUG: Tag display for condition {item['condition']}: '{tag_display}' (tags: {item['tags']})")
                        
                        line = (
                            f"{str(item['condition']).ljust(cond_w)}  "
                            f"{str(int(item['total_trades'])).rjust(trades_w)}  "
                            f"{self._format_drawdown_percent(item['max_drawdown']).rjust(drawdown_w)}  "
                            f"{self._format_number(item['profit_factor']).rjust(profit_w)}  "
                            f"{self._format_percent(item['win_rate']).rjust(winrate_w)}  "
                            f"{self._format_percent(item['net_profit_pct']).rjust(netprofit_w)}  "
                            f"{self._format_number(item['sharpe_ratio']).rjust(sharpe_w)}  "
                            f"{self._format_number(item['sortino_ratio']).rjust(sortino_w)}  "
                            f"{tag_display.ljust(tags_w)}"
                        )
                        lines.append(line)
                        
                        # Accumulate values for summary
                        total_trades_sum += int(item['total_trades'])
                        
                        # Collect valid numeric values (skip NaN/None)
                        if isinstance(item['max_drawdown'], (int, float)) and not (item['max_drawdown'] != item['max_drawdown']):  # not NaN
                            max_drawdown_values.append(item['max_drawdown'])
                        
                        if isinstance(item['profit_factor'], (int, float)) and not (item['profit_factor'] != item['profit_factor']):  # not NaN
                            profit_factor_values.append(item['profit_factor'])
                        
                        if isinstance(item['win_rate'], (int, float)) and not (item['win_rate'] != item['win_rate']):  # not NaN
                            win_rate_values.append(item['win_rate'])
                        
                        if isinstance(item['net_profit_pct'], (int, float)) and not (item['net_profit_pct'] != item['net_profit_pct']):  # not NaN
                            net_profit_values.append(item['net_profit_pct'])
                        
                        if isinstance(item['sharpe_ratio'], (int, float)) and not (item['sharpe_ratio'] != item['sharpe_ratio']):  # not NaN
                            sharpe_ratio_values.append(item['sharpe_ratio'])
                        
                        if isinstance(item['sortino_ratio'], (int, float)) and not (item['sortino_ratio'] != item['sortino_ratio']):  # not NaN
                            sortino_ratio_values.append(item['sortino_ratio'])
                    
                    # Calculate summary values
                    summary_max_drawdown = min(max_drawdown_values) if max_drawdown_values else 0  # Most negative (worst)
                    summary_profit_factor = sum(profit_factor_values) / len(profit_factor_values) if profit_factor_values else 0
                    summary_win_rate = sum(win_rate_values) / len(win_rate_values) if win_rate_values else 0
                    summary_net_profit = sum(net_profit_values) if net_profit_values else 0
                    summary_sharpe = sum(sharpe_ratio_values) / len(sharpe_ratio_values) if sharpe_ratio_values else 0
                    summary_sortino = sum(sortino_ratio_values) / len(sortino_ratio_values) if sortino_ratio_values else 0
                    
                    # Add summary row
                    lines.append(sep)
                    summary_line = (
                        f"{'TOTAL'.ljust(cond_w)}  "
                        f"{str(total_trades_sum).rjust(trades_w)}  "
                        f"{self._format_drawdown_percent(summary_max_drawdown).rjust(drawdown_w)}  "
                        f"{self._format_number(summary_profit_factor).rjust(profit_w)}  "
                        f"{self._format_percent(summary_win_rate).rjust(winrate_w)}  "
                        f"{self._format_percent(summary_net_profit).rjust(netprofit_w)}  "
                        f"{self._format_number(summary_sharpe).rjust(sharpe_w)}  "
                        f"{self._format_number(summary_sortino).rjust(sortino_w)}  "
                        f"{' '.ljust(tags_w)}"
                    )
                    lines.append(summary_line)
                else:
                    lines.append("(No single test data available)")
                lines.append("")

            # Conditions section
            lines.append("Conditions")
            lines.append("-" * len("Conditions"))
            if conditions:
                # Custom sort: numeric names first (1, 2, 10, ...), then alpha groups (e.g., dca1, dca2, ...)
                def _cond_sort_key(name: str):
                    n = str(name).strip()
                    if n.isdigit():
                        return (0, int(n), "", -1)
                    m = re.match(r'^([A-Za-z]+)(\d+)?$', n)
                    if m:
                        prefix = m.group(1)
                        num = int(m.group(2)) if m.group(2) else -1
                        return (1, prefix, num, -1)
                    return (2, n, -1, -1)

                # Prepare column widths
                cond_items = sorted(conditions.items(), key=lambda kv: _cond_sort_key(kv[0]))
                cond_col_w = max(len("Condition"), max(len(str(k)) for k, _ in cond_items))
                trig_col_w = max(len("Triggers"), max(len(str(v.get("Triggers time", ""))) for _, v in cond_items))
                entry_trig_w = max(
                    len("Entry triggers"),
                    max(len(str(v.get("Entry Triggers time", ""))) for _, v in cond_items),
                )
                dca_trig_w = max(
                    len("DCA triggers"),
                    max(len(str(v.get("DCA Triggers time", ""))) for _, v in cond_items),
                )
                entry_mdd_w = max(
                    len("Entry trigger MDD %"),
                    max(len(self._format_percent(v.get("Entry Trigger Max drawdown %", 0))) for _, v in cond_items),
                )
                dca_mdd_w = max(
                    len("DCA trigger MDD %"),
                    max(len(self._format_percent(v.get("DCA Trigger Max drawdown %", 0))) for _, v in cond_items),
                )
                dd_max_w = max(
                    len("Max drawdown %"),
                    max(len(self._format_percent(v.get("Max drawdown %", 0))) for _, v in cond_items),
                )
                win_rate_w = max(
                    len("Win rate (%)"),
                    max(len(self._format_percent(v.get("Win rate (%)", 0))) for _, v in cond_items),
                )

                header = (
                    f"{'Condition'.ljust(cond_col_w)}  "
                    f"{'Triggers'.rjust(trig_col_w)}  "
                    f"{'Entry triggers'.rjust(entry_trig_w)}  "
                    f"{'DCA triggers'.rjust(dca_trig_w)}  "
                    f"{'Entry trigger MDD %'.rjust(entry_mdd_w)}  "
                    f"{'DCA trigger MDD %'.rjust(dca_mdd_w)}  "
                    f"{'Max drawdown %'.rjust(dd_max_w)}  "
                    f"{'Win rate (%)'.rjust(win_rate_w)}"
                )
                sep = (
                    f"{'-' * cond_col_w}  "
                    f"{'-' * trig_col_w}  "
                    f"{'-' * entry_trig_w}  "
                    f"{'-' * dca_trig_w}  "
                    f"{'-' * entry_mdd_w}  "
                    f"{'-' * dca_mdd_w}  "
                    f"{'-' * dd_max_w}  "
                    f"{'-' * win_rate_w}"
                )
                lines.append(header)
                lines.append(sep)
                for key, stats in cond_items:
                    triggers = str(stats.get("Triggers time", ""))
                    entry_trigs = str(stats.get("Entry Triggers time", ""))
                    dca_trigs = str(stats.get("DCA Triggers time", ""))
                    entry_mdd = self._format_percent(stats.get("Entry Trigger Max drawdown %", 0))
                    dca_mdd = self._format_percent(stats.get("DCA Trigger Max drawdown %", 0))
                    dd_max = self._format_percent(stats.get("Max drawdown %", 0))
                    win_rate = self._format_percent(stats.get("Win rate (%)", 0))
                    line = (
                        f"{str(key).ljust(cond_col_w)}  "
                        f"{triggers.rjust(trig_col_w)}  "
                        f"{entry_trigs.rjust(entry_trig_w)}  "
                        f"{dca_trigs.rjust(dca_trig_w)}  "
                        f"{entry_mdd.rjust(entry_mdd_w)}  "
                        f"{dca_mdd.rjust(dca_mdd_w)}  "
                        f"{dd_max.rjust(dd_max_w)}  "
                        f"{win_rate.rjust(win_rate_w)}"
                    )
                    lines.append(line)
            else:
                lines.append("(No conditions)")
            lines.append("")

            # Positions section
            lines.append("Positions")
            lines.append("-" * len("Positions"))
            if positions:
                # Extract fields for table
                pos_rows = []
                for pos_key, info in positions.items():
                    dt = pos_key.replace("Position ", "", 1)
                    orders = info.get("orders", [])
                    orders_count = len(orders)
                    dd_value = info.get("Position max drawdown %", 0)
                    
                    # Get step conditions and sizes from ALL orders
                    step_conditions = []
                    size_percents = []
                    trade_numbers = []
                    
                    for order in orders:
                        signal = str(order.get("Signal", ""))
                        step_condition, size_percent = self._decode_signal(signal)
                        step_conditions.append(step_condition)
                        size_percents.append(size_percent)
                        
                        # Collect trade numbers
                        trade_num = order.get("Trade #", "")
                        if trade_num:
                            trade_numbers.append(str(trade_num))
                    
                    # Join with dashes
                    step_str = " - ".join(step_conditions)
                    size_str = " - ".join(size_percents)
                    trade_str = " - ".join(trade_numbers)
                    
                    pos_rows.append((dt, orders_count, dd_value, step_str, size_str, trade_str))
                
                # Sort positions by drawdown percentage (worst first)
                pos_rows.sort(key=lambda x: float(x[2]) if isinstance(x[2], (int, float)) else 0, reverse=False)

                # Column widths
                dt_w = max(len("Date/Time"), max(len(r[0]) for r in pos_rows))
                orders_w = max(len("Orders"), max(len(str(r[1])) for r in pos_rows))
                dd_w = max(len("DD %"), max(len(self._format_percent(r[2])) for r in pos_rows))
                step_w = max(len("Step"), max(len(r[3]) for r in pos_rows))
                size_w = max(len("Size %"), max(len(r[4]) for r in pos_rows))
                trade_w = max(len("Trade #"), max(len(r[5]) for r in pos_rows))

                header = f"{'Date/Time'.ljust(dt_w)}  {'Orders'.rjust(orders_w)}  {'DD %'.rjust(dd_w)}  {'Step'.ljust(step_w)}  {'Size %'.ljust(size_w)}  {'Trade #'.ljust(trade_w)}"
                sep = f"{'-' * dt_w}  {'-' * orders_w}  {'-' * dd_w}  {'-' * step_w}  {'-' * size_w}  {'-' * trade_w}"
                lines.append(header)
                lines.append(sep)

                for dt, orders_count, dd_value, step_str, size_str, trade_str in pos_rows:
                    line = f"{dt.ljust(dt_w)}  {str(orders_count).rjust(orders_w)}  {self._format_percent(dd_value).rjust(dd_w)}  {step_str.ljust(step_w)}  {size_str.ljust(size_w)}  {trade_str.ljust(trade_w)}"
                    lines.append(line)
            else:
                lines.append("(No positions)")
            lines.append("")

            content = "\n".join(lines)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True, output_path
        except Exception as e:
            return False, str(e)

    def export_excel(self, strategy_report: Dict[str, Any], file_name: str) -> Tuple[bool, str]:
        """
        Export analysis results to Excel report.
        
        Args:
            strategy_report: Analysis results dictionary
            file_name: Source Excel filename
            
        Returns:
            Tuple of (success, output_path or error_message)
        """
        try:
            # Save to cache
            self.save_cache(strategy_report, file_name)
            
            # Prepare output directory and filename
            reports_dir = get_data_directory("reports")
            ensure_directory(reports_dir)
            
            output_filename = os.path.splitext(file_name)[0] + ".xlsx"
            output_path = os.path.join(reports_dir, output_filename)
            
            # Handle both single report and multi-test report structures
            if "global_test" in strategy_report and "single_test" in strategy_report:
                # Multi-test structure
                global_data = strategy_report["global_test"]
                single_data = strategy_report["single_test"]
                positions = global_data.get("positions", {}) or {}
                conditions = global_data.get("conditions", {}) or {}
                total_positions = global_data.get("totalPositions", len(positions))
            else:
                # Single report structure
                positions = strategy_report.get("positions", {}) or {}
                conditions = strategy_report.get("conditions", {}) or {}
                total_positions = strategy_report.get("totalPositions", len(positions))
                single_data = None

            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # Summary sheet
                summary_data = {
                    'Metric': ['Source Sheet', 'Total Positions'],
                    'Value': [file_name, total_positions]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Single Test Performance sheet
                if single_data and isinstance(single_data, dict):
                    single_test_conditions = []
                    for condition_key, condition_data in single_data.items():
                        # Skip empty condition names
                        if not condition_key or str(condition_key).strip() == "":
                            continue
                            
                        if isinstance(condition_data, dict):
                            single_test_conditions.append({
                                'Condition': condition_key,
                                'Total Trades': condition_data.get("Total trades", 0),
                                'Max Drawdown %': condition_data.get("Max drawdown %", 0),
                                'Profit Factor': condition_data.get("Profit factor", 0),
                                'Win Rate %': condition_data.get("Percent profitable", 0),
                                'Net Profit %': condition_data.get("Net profit %", 0),
                                'Sharpe Ratio': condition_data.get("Sharpe ratio", 0),
                                'Sortino Ratio': condition_data.get("Sortino ratio", 0),
                                'Tags': ', '.join(condition_data.get("tags", [])) if condition_data.get("tags") else ''
                            })
                    
                    if single_test_conditions:
                        # Sort conditions numerically
                        def _single_test_sort_key(item):
                            condition = str(item["Condition"]).strip()
                            if condition.isdigit():
                                return (0, int(condition))
                            return (1, condition)
                        
                        single_test_conditions.sort(key=_single_test_sort_key)
                        
                        # Calculate summary metrics
                        total_trades_sum = sum(item['Total Trades'] for item in single_test_conditions)
                        
                        # Collect valid numeric values (skip NaN/None/empty strings)
                        max_drawdown_values = []
                        profit_factor_values = []
                        win_rate_values = []
                        net_profit_values = []
                        sharpe_ratio_values = []
                        sortino_ratio_values = []
                        
                        for item in single_test_conditions:
                            # Max Drawdown (most negative/worst)
                            if isinstance(item['Max Drawdown %'], (int, float)) and not (item['Max Drawdown %'] != item['Max Drawdown %']):
                                max_drawdown_values.append(item['Max Drawdown %'])
                            
                            # Profit Factor (average)
                            if isinstance(item['Profit Factor'], (int, float)) and not (item['Profit Factor'] != item['Profit Factor']):
                                profit_factor_values.append(item['Profit Factor'])
                            
                            # Win Rate (average)
                            if isinstance(item['Win Rate %'], (int, float)) and not (item['Win Rate %'] != item['Win Rate %']):
                                win_rate_values.append(item['Win Rate %'])
                            
                            # Net Profit (sum)
                            if isinstance(item['Net Profit %'], (int, float)) and not (item['Net Profit %'] != item['Net Profit %']):
                                net_profit_values.append(item['Net Profit %'])
                            
                            # Sharpe Ratio (average)
                            if isinstance(item['Sharpe Ratio'], (int, float)) and not (item['Sharpe Ratio'] != item['Sharpe Ratio']):
                                sharpe_ratio_values.append(item['Sharpe Ratio'])
                            
                            # Sortino Ratio (average)
                            if isinstance(item['Sortino Ratio'], (int, float)) and not (item['Sortino Ratio'] != item['Sortino Ratio']):
                                sortino_ratio_values.append(item['Sortino Ratio'])
                        
                        # Calculate summary values
                        summary_max_drawdown = min(max_drawdown_values) if max_drawdown_values else 0
                        summary_profit_factor = sum(profit_factor_values) / len(profit_factor_values) if profit_factor_values else 0
                        summary_win_rate = sum(win_rate_values) / len(win_rate_values) if win_rate_values else 0
                        summary_net_profit = sum(net_profit_values) if net_profit_values else 0
                        summary_sharpe = sum(sharpe_ratio_values) / len(sharpe_ratio_values) if sharpe_ratio_values else 0
                        summary_sortino = sum(sortino_ratio_values) / len(sortino_ratio_values) if sortino_ratio_values else 0
                        
                        # Add summary row
                        summary_row = {
                            'Condition': 'TOTAL',
                            'Total Trades': total_trades_sum,
                            'Max Drawdown %': summary_max_drawdown,
                            'Profit Factor': summary_profit_factor,
                            'Win Rate %': summary_win_rate,
                            'Net Profit %': summary_net_profit,
                            'Sharpe Ratio': summary_sharpe,
                            'Sortino Ratio': summary_sortino,
                            'Tags': ''
                        }
                        single_test_conditions.append(summary_row)
                        
                        single_df = pd.DataFrame(single_test_conditions)
                        single_df.to_excel(writer, sheet_name='Single Test Performance', index=False)
                
                # Conditions sheet
                if conditions:
                    conditions_data = []
                    for key, stats in conditions.items():
                        conditions_data.append({
                            'Condition': key,
                            'Triggers': stats.get("Triggers time", 0),
                            'Entry Triggers': stats.get("Entry Triggers time", 0),
                            'DCA Triggers': stats.get("DCA Triggers time", 0),
                            'Entry Trigger MDD %': stats.get("Entry Trigger Max drawdown %", 0),
                            'DCA Trigger MDD %': stats.get("DCA Trigger Max drawdown %", 0),
                            'Max Drawdown %': stats.get("Max drawdown %", 0),
                            'Win Rate (%)': stats.get("Win rate (%)", 0)
                        })
                    
                    # Sort conditions
                    def _cond_sort_key(item):
                        name = str(item['Condition']).strip()
                        if name.isdigit():
                            return (0, int(name), "", -1)
                        m = re.match(r'^([A-Za-z]+)(\d+)?$', name)
                        if m:
                            prefix = m.group(1)
                            num = int(m.group(2)) if m.group(2) else -1
                            return (1, prefix, num, -1)
                        return (2, name, -1, -1)
                    
                    conditions_data.sort(key=_cond_sort_key)
                    conditions_df = pd.DataFrame(conditions_data)
                    conditions_df.to_excel(writer, sheet_name='Conditions', index=False)
                
                # Positions sheet
                if positions:
                    positions_data = []
                    for pos_key, info in positions.items():
                        dt = pos_key.replace("Position ", "", 1)
                        orders = info.get("orders", [])
                        orders_count = len(orders)
                        dd_value = info.get("Position max drawdown %", 0)
                        
                        # Get step conditions and sizes from ALL orders
                        step_conditions = []
                        size_percents = []
                        trade_numbers = []
                        
                        for order in orders:
                            signal = str(order.get("Signal", ""))
                            step_condition, size_percent = self._decode_signal(signal)
                            step_conditions.append(step_condition)
                            size_percents.append(size_percent)
                            
                            # Collect trade numbers
                            trade_num = order.get("Trade #", "")
                            if trade_num:
                                trade_numbers.append(str(trade_num))
                        
                        # Join with dashes
                        step_str = " - ".join(step_conditions)
                        size_str = " - ".join(size_percents)
                        trade_str = " - ".join(trade_numbers)
                        
                        positions_data.append({
                            'Date/Time': dt,
                            'Orders': orders_count,
                            'DD %': dd_value,
                            'Step': step_str,
                            'Size %': size_str,
                            'Trade #': trade_str
                        })
                    
                    # Sort positions by drawdown percentage (worst first)
                    positions_data.sort(key=lambda x: float(x['DD %']) if isinstance(x['DD %'], (int, float)) else 0, reverse=False)
                    positions_df = pd.DataFrame(positions_data)
                    positions_df.to_excel(writer, sheet_name='Positions', index=False)
                
                # Performance Metrics sheet (if available)
                performance_metrics = {}
                for key, value in strategy_report.items():
                    if key not in ['orders', 'positions', 'totalPositions', 'conditions', 'Max drawdown %', 'Net profit %']:
                        if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit()):
                            try:
                                performance_metrics[key] = float(value)
                            except:
                                performance_metrics[key] = value
                
                if performance_metrics:
                    perf_df = pd.DataFrame(list(performance_metrics.items()), columns=['Metric', 'Value'])
                    perf_df.to_excel(writer, sheet_name='Performance Metrics', index=False)

            return True, output_path
        except Exception as e:
            return False, str(e)

    def exports(self, results: Dict[str, Any], filename: str):
        """
        Export analysis results to report files (TXT and Excel).
        
        Args:
            results: Analysis results dictionary
            filename: Original Excel filename
        """
        print(f"🔄 Merging with cached data for: {filename}")
        cached_data = self.load_cache(filename)
        
        if cached_data:
            # Merge results with cached data
            merged_results = self._merge_with_cache(results, cached_data)
            results = merged_results
            print(f"✅ Merged with existing cache data")
        else:
            print(f"⚠️  No cache found, using fresh data")
        
        # Export to TXT format
        txt_success, txt_path = self.export_txt(results, filename)
        if txt_success:
            print(f"📄 TXT report saved to: {txt_path}")
        else:
            print(f"❌ TXT report export failed: {txt_path}")
        
        # Export to Excel format
        excel_success, excel_path = self.export_excel(results, filename)
        if excel_success:
            print(f"📊 Excel report saved to: {excel_path}")
        else:
            print(f"❌ Excel report export failed: {excel_path}")
    
    def _merge_with_cache(self, new_results: Dict[str, Any], cached_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge new results with cached data, preserving existing single test data.
        
        Args:
            new_results: New analysis results
            cached_data: Existing cached data
            
        Returns:
            Merged results dictionary
        """
        merged = cached_data.copy()
        
        # Always update global test data
        if "global_test" in new_results:
            merged["global_test"] = new_results["global_test"]
            print(f"🔄 Updated global test data")
        
        # Merge single test data intelligently
        if "single_test" in new_results:
            if "single_test" not in merged:
                merged["single_test"] = {}
            
            # Get conditions to update from config
            conditions_to_update = self.config.get("TOTAL_CONDITIONS", [])
            print(f"📋 Updating conditions: {conditions_to_update}")
            
            for condition_key, condition_data in new_results["single_test"].items():
                if condition_key in conditions_to_update:
                    # Check if condition data is empty/empty string
                    if not condition_data or condition_data == "":
                        # Use global test data instead
                        if "global_test" in new_results:
                            merged["single_test"][condition_key] = new_results["global_test"]
                            print(f"🔄 Condition {condition_key}: Using global test data (condition was empty)")
                        else:
                            print(f"⚠️  Condition {condition_key}: Empty and no global test available")
                    else:
                        # Update with new condition data
                        merged["single_test"][condition_key] = condition_data
                        print(f"🔄 Condition {condition_key}: Updated with new data")
                else:
                    # Keep existing data for conditions not in config
                    if condition_key in merged["single_test"]:
                        print(f"💾 Condition {condition_key}: Preserved existing data")
                    else:
                        # Add new condition data
                        merged["single_test"][condition_key] = condition_data
                        print(f"➕ Condition {condition_key}: Added new data")
        
        return merged

    def _format_percent(self, value: float) -> str:
        """Format value as percentage string."""
        try:
            return f"{float(value):.3f}%"
        except Exception:
            return str(value)

    def _format_drawdown_percent(self, value: float) -> str:
        """Format drawdown value as percentage string."""
        try:
            # Convert from raw value to percentage if needed
            val = float(value)
            if val > 0:
                val = -val  # Drawdown should be negative
            return f"{val:.2f}%"
        except Exception:
            return str(value)

    def _format_number(self, value: float) -> str:
        """Format number with appropriate decimal places."""
        try:
            val = float(value)
            if val >= 100:
                return f"{val:.1f}"
            elif val >= 10:
                return f"{val:.2f}"
            else:
                return f"{val:.3f}"
        except Exception:
            return str(value)

    def _format_size_equity(self, value: float) -> str:
        """Format size equity as percentage string."""
        try:
            pct = float(value) * 100.0
            if abs(pct - round(pct)) < 1e-9:
                return str(int(round(pct)))
            # Trim trailing zeros
            s = f"{pct:.2f}"
            return s.rstrip('0').rstrip('.')
        except Exception:
            return str(value)

    def _decode_signal(self, signal: str) -> Tuple[str, str]:
        """Decode signal into condition and size components."""
        try:
            data = encode_signals(signal)
            step_condition = str(data.get("conditions", "")).strip()
            size_equity = data.get("sizeEquity", "")
            size_str = ""
            if size_equity != "":
                size_str = self._format_size_equity(size_equity)
            return step_condition, size_str
        except Exception:
            return signal.strip(), ""
