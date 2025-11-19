"""
Async version of embedding module for parallel LMM execution
Supports cursor-agent, GitHub Copilot CLI, and Amazon Q Developer CLI
"""
import asyncio
import os
from typing import Optional, Dict, Any, Literal
from src.utils.lmm_utils import decode_LMM_output
from train.scripts_cli import get_tool_script
from config import STRATEGY_SETTINGS


async def run_strategy_embedding(
    *,
    name: Optional[str] = None,
    base_condition_name: str = "openLong",
    condition_id: str = "7",
    time_backtest: Optional[str] = None,
    net_profit_percent: Optional[str] = None,
    max_drawdown_percent: Optional[str] = None,
    total_trades: Optional[int] = None,
    percent_profitable: Optional[str] = None,
    target: Optional[Dict[str, Any]] = None,
    check: bool = False,
    timeout: int = 250,
    assitent_comment_before: str = "",
    command: str = "agent",
    pinescript_path: str = "train/dev.pine",
    tool: Literal["cursor-agent", "copilot", "amazon-q"] = "cursor-agent",
    model: Optional[str] = None,
    stream_logs: bool = False
) -> dict:
    """Build and run AI coding agent prompt with cursor-agent, copilot, or Amazon Q.

    Args:
        name: Asset name (default from STRATEGY_SETTINGS)
        base_condition_name: Base condition variable name
        condition_id: Condition identifier
        time_backtest: Backtest time period
        net_profit_percent: Net profit percentage from backtest
        max_drawdown_percent: Max drawdown percentage from backtest
        total_trades: Total number of trades
        percent_profitable: Percentage of profitable trades
        target: Target criteria dict
        check: Check mode flag
        timeout: Process timeout in seconds
        assitent_comment_before: Previous assistant comments
        command: Command type for cursor-agent ("agent", "chat")
        pinescript_path: Path to PineScript file
        tool: Choose "cursor-agent", "copilot", or "amazon-q"
        model: Model to use (cursor-agent: "grok", "claude-sonnet-4")
        stream_logs: Enable real-time log streaming

    Returns:
        Decoded LMM output dict
    """
    # Use strategy settings as defaults
    name = name or STRATEGY_SETTINGS.get("asset_name", "XAU")
    time_backtest = time_backtest or STRATEGY_SETTINGS.get("time_backtest", "2009 -> present")
    target = target or STRATEGY_SETTINGS.get("target_criteria", {
        "total_trades_min": 85, 
        "max_drawdown_max": 30
    })

    # Build variable names and result lines
    cond_var = f"{base_condition_name}{condition_id}"
    trades_line = f"- Total trades: {total_trades}" if total_trades is not None else "- Total trades:"
    dd_line = f"- Max Drawdown (%): {max_drawdown_percent}" if max_drawdown_percent is not None else "- Max Drawdown (%):"
    np_line = f"- Net Profit (%): {net_profit_percent}" if net_profit_percent is not None else "- Net Profit (%):"
    pp_line = f"- Percent profitable: {percent_profitable}" if percent_profitable is not None else "- Percent profitable:"

    # Get prompt template from settings
    prompt_template = STRATEGY_SETTINGS.get("prompt_template", {})

    # Build the main prompt
    prompt = f"""
# Context
[Just EDIT the code in @{pinescript_path} and not talking anything else]
{prompt_template.get("context", "You are an AI agent specialized in PineScript code optimization.")}
Your task is to edit/write the given PineScript strategy so that the backtest results meet the target condition.

{prompt_template.get("asset_description", f"{name} can be long in some situation like:\n- trend following")}

Learn logic and function in train/pinescripts_docs/pinescript_docs.md and use it to optimize the logic of `{cond_var}`

# Backtest Result (Single Test for {cond_var})
- Time: {time_backtest}
{dd_line}
{trades_line}
{pp_line}
{np_line}

# Rule & Solution
- Make sure condition [{condition_id}] is NOT same / in-relation / in-range / conflic LOGIC with other {base_condition_name}s
  Example: already have a >= b => no use anymore. open1 = rsi50_30M >= 50 so only use rsi50_30M < 50
  NOT use >= 45 or >=45 <= 60..., it's IN-RANGE and in same Direction
- In {cond_var} only use maximum 3 logic conditions
- Don't look at results or logic in another file, only focus on @{pinescript_path}
- If condition has mdd <= -100%, try to add more conditions to reduce mdd
- Keep strategy logic limited to variables already defined in request_security
- You can define more variables in request_security but keep same output rules
- Some special indicators like supertrend, bb, dmi... return array of results
  Need to define as variables first then put single variable with [offset] to avoid repaint
  Example:
  ```
  [a,b,c] = ta.dmi(m,n)
  a_30M, b_30M, c_30M = request.security(tickerid, T30m, [a[offset], b[offset], c[offset]], lookahead = lookahead_type)
  ```
- No define variable already defined
- Define new request_security variables before {cond_var} for easy debug
- Avoid repainting, overfitting, and data snooping
- Be creative and think outside the box

# Strategy-Specific Optimization Focus
{prompt_template.get("optimization_focus", "Focus on general trading principles and market dynamics.")}

# Risk Considerations
{prompt_template.get("risk_considerations", "Consider general risk management principles.")}

# Optimization Goal (Condition [{condition_id}])
- Net Profit ≥ {target.get("net_profit_min", 100)}%
- Max Drawdown ≥ {-abs(target.get("max_drawdown_max", -30))}%
- Total trades ≥ {target.get("total_trades_min", 85)}

# Assistant Comment Before
{assitent_comment_before if assitent_comment_before != "" else "No comment before"}

# Task
1. Analyze the given PineScript strategy and current backtest results (@{pinescript_path})
2. Write/Rewrite the **code logic** of `{cond_var}` in @{pinescript_path} to get target
""".strip()

    # Generate bash script using utility module
    try:
        bash_script = get_tool_script(
            tool=tool,
            prompt=prompt,
            command=command,
            model=model,
            allow_all_tools=True,
            accept_all=True,
            no_interactive=True
        )
    except ValueError as e:
        print(f"❌ {str(e)}")
        return {}

    # Execute the subprocess
    try:
        proc = await asyncio.create_subprocess_shell(
            bash_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )

        if stream_logs:
            # Real-time streaming mode
            async def read_stream(stream, prefix):
                """Read and print stream line by line in real-time."""
                lines = []
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded = line.decode('utf-8', errors='ignore').rstrip()
                    print(f"{prefix}: {decoded}")
                    lines.append(decoded)
                return "\n".join(lines)

            try:
                stdout_str, stderr_str, _ = await asyncio.wait_for(
                    asyncio.gather(
                        read_stream(proc.stdout, f"[{tool}]"),
                        read_stream(proc.stderr, f"[{tool} ERR]"),
                        proc.wait()
                    ),
                    timeout=timeout
                )

                if stderr_str:
                    print(f"\n⚠️ [{tool}] stderr output detected")

                return decode_LMM_output(stdout_str)

            except asyncio.TimeoutError:
                print(f"⚠️ {tool} timed out after {timeout}s, killing process")
                proc.kill()
                await proc.wait()
                return {}

        else:
            # Wait for completion mode (no streaming)
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )

                stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else ""
                stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else ""

                if stderr_str:
                    print(f"[{tool} stderr]: {stderr_str}")

                return decode_LMM_output(stdout_str)

            except asyncio.TimeoutError:
                print(f"⚠️ {tool} timed out after {timeout}s, killing process")
                proc.kill()
                await proc.wait()
                return {}

    except Exception as e:
        print(f"❌ Error running {tool}: {str(e)}")
        return {}


def load_pine_code(path: Optional[str] = None, name: Optional[str] = None) -> str:
    """Load Pine Script code from file (synchronous function).

    Args:
        path: Full path to file (optional)
        name: Filename (optional, default: "dev.pine")

    Returns:
        File content as string, empty string on error
    """
    try:
        default_path = os.path.join(
            os.path.dirname(__file__), 
            name if name else "dev.pine"
        )
    except Exception:
        return ""

    try:
        target_path = path or default_path
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


__all__ = ["run_strategy_embedding", "load_pine_code"]
