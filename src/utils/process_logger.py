"""
Reusable Rich logging system for parallel process monitoring
"""

from rich.live import Live
from rich.table import Table
from rich.console import Console
from collections import defaultdict
from typing import Any, Dict, Optional
import threading
import asyncio
from datetime import datetime


class ProcessLogger:
    """Thread-safe logger for tracking multiple parallel processes with Rich table display"""
    
    def __init__(self):
        self.process_logs = defaultdict(lambda: {
            'status': 'INIT',
            'iteration': 0,
            'trades': 'N/A',
            'drawdown': 'N/A',
            'net_profit': 'N/A',
            'message': '',
            'errors': 0,
            'last_update': ''
        })
        self.log_lock = threading.Lock()
        self.console = Console()
        self.live_display = None
        self.display_task = None
        
    def update(self, process_name: str, **kwargs):
        """
        Thread-safe update of process log data
        
        Args:
            process_name: Identifier for the process
            **kwargs: Fields to update (status, iteration, trades, drawdown, net_profit, message, errors)
        """
        with self.log_lock:
            self.process_logs[process_name].update(kwargs)
            self.process_logs[process_name]['last_update'] = datetime.now().strftime("%H:%M:%S")
    
    def create_table(self) -> Table:
        """Create a Rich table showing all process logs"""
        table = Table(
            title="Trading Strategy Optimization - Live Status",
            show_header=True,
            header_style="bold cyan",
            border_style="dim"
        )
        
        table.add_column("Process", style="cyan", width=15)
        table.add_column("Status", style="white", width=10)
        table.add_column("Iter", justify="right", style="yellow", width=6)
        table.add_column("Trades", justify="right", style="blue", width=8)
        table.add_column("DD%", justify="right", style="red", width=10)
        table.add_column("NP%", justify="right", style="green", width=10)
        table.add_column("Errors", justify="right", style="red", width=7)
        table.add_column("Last Update", style="dim", width=10)
        table.add_column("Message", style="white", width=45)
        
        with self.log_lock:
            for process_name in sorted(self.process_logs.keys()):
                log = self.process_logs[process_name]
                
                # Status formatting
                status = log['status']
                if status == 'RUNNING':
                    status_display = "[green]RUNNING[/green]"
                elif status == 'DONE':
                    status_display = "[blue]DONE[/blue]"
                elif status == 'ERROR':
                    status_display = "[red]ERROR[/red]"
                else:
                    status_display = "[yellow]INIT[/yellow]"
                
                # Format numeric values
                drawdown = str(log['drawdown'])
                net_profit = str(log['net_profit'])
                
                table.add_row(
                    process_name,
                    status_display,
                    str(log['iteration']),
                    str(log['trades']),
                    drawdown,
                    net_profit,
                    str(log['errors']),
                    log['last_update'],
                    log['message'][:45]
                )
        
        return table
    
    async def start_live_display(self):
        """Start live table display with auto-refresh"""
        self.live_display = Live(
            self.create_table(),
            refresh_per_second=2,
            console=self.console
        )
        self.live_display.start()
        
        # Start background update task
        async def update_display():
            while True:
                try:
                    self.live_display.update(self.create_table())
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    break
        
        self.display_task = asyncio.create_task(update_display())
    
    async def stop_live_display(self):
        """Stop live display and show final table"""
        if self.display_task:
            self.display_task.cancel()
            try:
                await self.display_task
            except asyncio.CancelledError:
                pass
        
        if self.live_display:
            self.live_display.update(self.create_table())
            self.live_display.stop()
    
    def log(self, process_name: str, message: str, level: str = "INFO"):
        """
        Simple log method for backward compatibility
        
        Args:
            process_name: Process identifier
            message: Log message
            level: Log level (INFO, WARNING, ERROR)
        """
        self.update(process_name, message=f"[{level}] {message}")
    
    def get_process_data(self, process_name: str) -> Dict[str, Any]:
        """Get current data for a specific process"""
        with self.log_lock:
            return self.process_logs.get(process_name, {}).copy()
    
    def clear(self):
        """Clear all process logs"""
        with self.log_lock:
            self.process_logs.clear()


# Global singleton instance
_global_logger: Optional[ProcessLogger] = None


def get_logger() -> ProcessLogger:
    """Get or create global ProcessLogger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ProcessLogger()
    return _global_logger


def init_logger() -> ProcessLogger:
    """Initialize and return new ProcessLogger instance"""
    global _global_logger
    _global_logger = ProcessLogger()
    return _global_logger
