"""
Excel data reading and processing utilities.
"""

import pandas as pd
from typing import List, Dict, Any


class ExcelReader:
    """Excel file reader and processor."""
    
    @staticmethod
    def read_worksheet_as_json(file_path: str, sheet_index: int = 0) -> List[Dict[str, Any]]:
        """
        Read Excel worksheet and convert to JSON format.
        
        Args:
            file_path: Path to Excel file
            sheet_index: Index of sheet to read (0-based)
            
        Returns:
            List of dictionaries representing worksheet data
            
        Raises:
            FileNotFoundError: If Excel file doesn't exist
            IndexError: If sheet index is invalid
        """
        try:
            # Get sheet names
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            if sheet_index >= len(sheet_names):
                raise IndexError(f"Sheet index {sheet_index} out of range. Available sheets: {sheet_names}")
            
            # Read the specified sheet
            df = pd.read_excel(file_path, sheet_name=sheet_names[sheet_index])
            
            # Convert datetime columns to strings for JSON serialization
            for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
                df[col] = df[col].astype(str)
            
            return df.to_dict(orient="records")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading Excel file: {e}")
    
    @staticmethod
    def get_sheet_names(file_path: str) -> List[str]:
        """
        Get all sheet names from Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise Exception(f"Error getting sheet names: {e}")
    
    @staticmethod
    def merge_orders_to_positions(orders_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge Entry and Exit orders into positions.
        
        Args:
            orders_data: List of order dictionaries
            
        Returns:
            List of position dictionaries with merged data
        """
        positions = {}
        
        for order in orders_data:
            trade_num = order.get('Trade #')
            order_type = order.get('Type', '')
            
            if trade_num not in positions:
                positions[trade_num] = {
                    'Trade #': trade_num,
                    'Entry': None,
                    'Exit': None
                }
            
            if 'Entry' in order_type:
                positions[trade_num]['Entry'] = order
            elif 'Exit' in order_type:
                positions[trade_num]['Exit'] = order
        
        # Convert to list and create merged positions
        positions_list = []
        for trade_num, position in positions.items():
            if position['Entry'] and position['Exit']:
                entry = position['Entry']
                exit_order = position['Exit']
                
                merged_position = {
                    'Trade #': trade_num,
                    'Entry Date/Time': entry.get('Date/Time'),
                    'Exit Date/Time': exit_order.get('Date/Time'),
                    'Entry Price USDT': entry.get('Price USDT'),
                    'Exit Price USDT': exit_order.get('Price USDT'),
                    'Entry Signal': entry.get('Signal'),
                    'Exit Signal': exit_order.get('Signal'),
                    'Position size (qty)': exit_order.get('Position size (qty)'),
                    'Position size (value)': exit_order.get('Position size (value)'),
                    'P&L USD': exit_order.get('P&L USD'),
                    'P&L %': exit_order.get('P&L %'),
                    'Run-up USD': exit_order.get('Run-up USD'),
                    'Run-up %': exit_order.get('Run-up %'),
                    'Drawdown USD': exit_order.get('Drawdown USD'),
                    'Drawdown %': exit_order.get('Drawdown %'),
                    'Cumulative P&L USD': exit_order.get('Cumulative P&L USD'),
                    'Cumulative P&L %': exit_order.get('Cumulative P&L %')
                }
                positions_list.append(merged_position)
        
        return positions_list
