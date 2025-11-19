"""Configuration management with runtime parameter overrides."""

import os
from typing import Dict, Any, List


class ConfigManager:
    """Manages configuration with CLI overrides."""
    
    def __init__(self, config_path: str = "config.py"):
        self.config_path = config_path
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        config_globals = {}
        with open(self.config_path, 'r') as f:
            exec(f.read(), config_globals)
        
        self._config = {
            key: value for key, value in config_globals.items()
            if not key.startswith('__')
        }
    
    def override_strategy(self, strategy_key: str):
        """Switch to different strategy (xau-long, btc-long, etc)."""
        if strategy_key not in self._config['LIST_STRATEGY_SETTINGS']:
            available = list(self._config['LIST_STRATEGY_SETTINGS'].keys())
            raise ValueError(f"Strategy '{strategy_key}' not found. Available: {available}")
        
        settings = self._config['LIST_STRATEGY_SETTINGS'][strategy_key]
        self._config['STRATEGY_SETTINGS'] = settings
        self._config['STRATEGY_NAME'] = settings['strategy_name']
        self._config['SYMBOL'] = settings['symbol']
        self._config['TARGET_CRITERIA'] = settings['target_criteria']
        self._config['TARGET_POTENTIAL'] = settings['target_potential']
        self._config['ASSET_NAME'] = settings['asset_name']
        self._config['TIME_BACKTEST'] = settings['time_backtest']
    
    def override_total_conditions(self, conditions: List[str]):
        """Set TOTAL_CONDITIONS list."""
        self._config['TOTAL_CONDITIONS'] = conditions
    
    def override_param(self, key: str, value: Any):
        """Override any config parameter."""
        self._config[key] = value
    
    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()
    
    def get(self, key: str, default=None):
        return self._config.get(key, default)
    
    def display_config(self):
        """Show current config summary."""
        print("\n" + "="*50)
        print("CONFIG SUMMARY")
        print("="*50)
        print(f"Strategy: {self._config.get('STRATEGY_NAME')}")
        print(f"Asset: {self._config.get('ASSET_NAME')}")
        print(f"Conditions: {self._config.get('TOTAL_CONDITIONS')}")
        print(f"Max Iter: {self._config.get('MAX_ITERATIONS')}")
        print(f"Processes: {self._config.get('PROCESS_COUNT')}")
        print("="*50 + "\n")
