#!/usr/bin/env python3
"""
Trading Analytics Tool - Main Entry Point
Run optimization or evaluation with flexible CLI configuration.
"""

import argparse
import asyncio
from pathlib import Path
import sys


def parse_conditions(conditions_str: str) -> list:
    """Parse condition string into list. Supports: '1,3,6' or '1-10' or '1,3-5,8'"""
    conditions = []
    parts = conditions_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            conditions.extend([str(i) for i in range(start, end + 1)])
        else:
            conditions.append(part)
    
    return conditions


def run_optimize(args):
    """Run optimization with config overrides."""
    from optimise import run_strategy_agent
    from utils.config_manager import ConfigManager
    
    config_manager = ConfigManager("config.py")
    
    if args.strategy:
        config_manager.override_strategy(args.strategy)
    
    if args.conditions:
        conditions = parse_conditions(args.conditions)
        config_manager.override_total_conditions(conditions)
    
    if args.max_iterations:
        config_manager.override_param('MAX_ITERATIONS', args.max_iterations)
    
    if args.process_count:
        config_manager.override_param('PROCESS_COUNT', args.process_count)
    
    if args.max_drawdown:
        target = config_manager.get('TARGET_CRITERIA', {})
        target['max_drawdown_max'] = args.max_drawdown
        config_manager.override_param('TARGET_CRITERIA', target)
    
    if args.min_trades:
        target = config_manager.get('TARGET_CRITERIA', {})
        target['total_trades_min'] = args.min_trades
        config_manager.override_param('TARGET_CRITERIA', target)

    if args.tool:
        config_manager.override_param('TOOL', args.tool)

    config_manager.display_config()
    asyncio.run(run_strategy_agent(config_manager.get_config()))


def run_evaluate(args):
    """Run evaluation with config overrides."""
    from evaluate import main as evaluate_main
    from utils.config_manager import ConfigManager
    
    config_manager = ConfigManager("config.py")
    
    if args.strategy:
        config_manager.override_strategy(args.strategy)
    
    if args.conditions:
        conditions = parse_conditions(args.conditions)
        config_manager.override_total_conditions(conditions)
    
    config_manager.display_config()
    asyncio.run(evaluate_main(config_manager.get_config()))


def main():
    parser = argparse.ArgumentParser(
        description='Trading Analytics Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python m.py optimize --strategy btc-long
  python m.py optimize --conditions "1,3,6"
  python m.py optimize --conditions "1-26"
  python m.py optimize --strategy xau-long --conditions "1-10" --max-iterations 100
  python m.py evaluate --strategy eth-long
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Mode')
    
    # Optimize
    opt = subparsers.add_parser('optimize', help='Run optimization')
    opt.add_argument('--strategy', '-s', help='Strategy: xau-long, btc-long, btc-short, eth-long')
    opt.add_argument('--conditions', '-c', help='Conditions: "1,3,6" or "1-26"')
    opt.add_argument('--max-iterations', '-i', type=int, help='Max iterations')
    opt.add_argument('--process-count', '-p', type=int, help='Parallel processes')
    opt.add_argument('--tool', '-t', type=str, help='Tools: cursor-agent, q-amazon, copilot, gemini')

    opt.add_argument('--max-drawdown', type=float, help='Max drawdown %')
    opt.add_argument('--min-trades', type=int, help='Min trades required')
    
    # Evaluate
    ev = subparsers.add_parser('evaluate', help='Run evaluation')
    ev.add_argument('--strategy', '-s', help='Strategy key')
    ev.add_argument('--conditions', '-c', help='Conditions to evaluate')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        sys.exit(1)
    
    if args.mode == 'optimize':
        run_optimize(args)
    elif args.mode == 'evaluate':
        run_evaluate(args)


if __name__ == "__main__":
    main()
