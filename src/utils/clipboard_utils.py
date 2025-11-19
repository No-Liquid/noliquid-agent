"""
Clipboard utilities for copying code and text to system clipboard.
"""

import pyperclip
import os
from typing import Optional


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to the system clipboard.
    
    Args:
        text (str): The text to copy to clipboard
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False


def copy_file_to_clipboard(file_path: str) -> bool:
    """
    Copy the contents of a file to the system clipboard.
    
    Args:
        file_path (str): Path to the file to copy
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        return copy_to_clipboard(content)
    except Exception as e:
        print(f"Error reading file and copying to clipboard: {e}")
        return False


def copy_strategy_code_to_clipboard(strategy_code: str, strategy_name: Optional[str] = None) -> bool:
    """
    Copy Pine Script strategy code to clipboard with optional formatting.
    
    Args:
        strategy_code (str): The Pine Script code to copy
        strategy_name (str, optional): Name of the strategy for context
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add strategy name as comment if provided
        if strategy_name:
            formatted_code = f"// Strategy: {strategy_name}\n\n{strategy_code}"
        else:
            formatted_code = strategy_code
            
        return copy_to_clipboard(formatted_code)
    except Exception as e:
        print(f"Error copying strategy code to clipboard: {e}")
        return False


def get_clipboard_content() -> str:
    """
    Get the current content of the system clipboard.
    
    Returns:
        str: Clipboard content, empty string if error
    """
    try:
        return pyperclip.paste()
    except Exception as e:
        print(f"Error reading from clipboard: {e}")
        return ""


if __name__ == "__main__":
    # Example usage
    sample_code = """
//@version=5
strategy("Sample Strategy", overlay=true)

// Simple moving average crossover
sma20 = ta.sma(close, 20)
sma50 = ta.sma(close, 50)

// Entry conditions
long_condition = ta.crossover(sma20, sma50)
short_condition = ta.crossunder(sma20, sma50)

// Execute trades
if long_condition
    strategy.entry("Long", strategy.long)

if short_condition
    strategy.entry("Short", strategy.short)
"""
    
    print("Testing clipboard functionality...")
    
    # Test copying strategy code
    success = copy_strategy_code_to_clipboard(sample_code, "Sample MA Crossover")
    
    if success:
        print("✅ Strategy code copied to clipboard successfully!")
        print("You can now paste it in TradingView or any other application.")
        
        # Verify by reading back
        clipboard_content = get_clipboard_content()
        if clipboard_content:
            print(f"📋 Clipboard contains {len(clipboard_content)} characters")
    else:
        print("❌ Failed to copy to clipboard")