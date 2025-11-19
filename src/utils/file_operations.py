"""
Utility functions for file operations.
"""

import os
from typing import List, Optional


def get_data_directory(subdirectory: str = "sheets") -> str:
    """
    Get path to data directory.
    
    Args:
        subdirectory: Name of subdirectory under data/
        
    Returns:
        Path to data directory
    """
    return os.path.join(os.getcwd(), "data", subdirectory)


def find_excel_files(directory_path: str) -> List[str]:
    """
    Find all Excel files in directory.
    
    Args:
        directory_path: Directory to search
        
    Returns:
        List of Excel filenames
    """
    if not os.path.exists(directory_path):
        return []
    
    excel_files = []
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.xlsx', '.xls')):
            excel_files.append(filename)
    
    return sorted(excel_files)


def get_file_path(directory: str, filename: str) -> str:
    """
    Get full file path.
    
    Args:
        directory: Directory path
        filename: Filename
        
    Returns:
        Full file path
    """
    return os.path.join(directory, filename)


def ensure_directory(directory_path: str):
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory_path: Directory path to ensure
    """
    os.makedirs(directory_path, exist_ok=True)
