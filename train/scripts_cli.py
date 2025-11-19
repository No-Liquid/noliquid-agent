"""
Utility module for AI coding tool bash script generation
Supports cursor-agent, GitHub Copilot CLI, and Amazon Q Developer CLI
"""
from typing import Optional, Literal


def generate_cursor_agent_script(prompt: str, command: str = "agent", model: Optional[str] = None) -> str:
    """Generate bash script for cursor-agent CLI.

    Args:
        prompt: The prompt to send to cursor-agent
        command: Command type (e.g., "agent", "chat")
        model: Model to use (e.g., "grok", "claude-sonnet-4")

    Returns:
        Complete bash script as string
    """
    model_flag = f"--model {model}" if model else ""

    script = f"""
set -e
if command -v cursor-agent >/dev/null 2>&1 || [ -x "$HOME/.local/bin/cursor-agent" ]; then
    echo "cursor-agent already installed"
else
    curl https://cursor.com/install -fsS | bash
fi

if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
fi

if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

export PATH="$HOME/.local/bin:$PATH"
cursor-agent --version || true

cursor-agent {command} {model_flag} <<'EOF'
{prompt}
/exit
EOF
""".strip()

    return script


def generate_copilot_script(prompt: str, allow_all_tools: bool = True) -> str:
    """Generate bash script for GitHub Copilot CLI.

    Args:
        prompt: The prompt to send to copilot
        allow_all_tools: If True, auto-approve all tool usage

    Returns:
        Complete bash script as string
    """
    # Escape single quotes in prompt for bash
    escaped_prompt = prompt.replace("'", "'\\''")
    tools_flag = "--allow-all-tools" if allow_all_tools else ""

    script = f"""
set -e
if ! command -v copilot >/dev/null 2>&1; then
    npm install -g @github/copilot
fi

copilot -p '{escaped_prompt}' {tools_flag}
""".strip()

    return script


def generate_amazon_q_script(prompt: str, accept_all: bool = True, no_interactive: bool = True) -> str:
    """Generate bash script for Amazon Q Developer CLI.

    Args:
        prompt: The prompt to send to Amazon Q
        accept_all: If True, auto-approve all tool usage (-a flag)
        no_interactive: If True, run in non-interactive mode (exit after response)

    Returns:
        Complete bash script as string
    """
    # Escape single quotes in prompt for bash
    escaped_prompt = prompt.replace("'", "'\\''")

    # Build flags
    flags = []
    if accept_all:
        flags.append("-a")
    if no_interactive:
        flags.append("--no-interactive")
    flags_str = " ".join(flags)

    script = f"""
set -e
if ! command -v q >/dev/null 2>&1; then
    # Install Amazon Q CLI
    curl --proto '=https' --tlsv1.2 -sSf "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-x86_64-linux.zip" -o "q.zip"
    unzip -q q.zip
    ./q/install.sh --non-interactive || true

    # Add to PATH
    export PATH="$HOME/q/bin:$PATH"
    if ! grep -q 'export PATH="$HOME/q/bin:$PATH"' ~/.bashrc 2>/dev/null; then
        echo 'export PATH="$HOME/q/bin:$PATH"' >> ~/.bashrc
    fi
    if ! grep -q 'export PATH="$HOME/q/bin:$PATH"' ~/.zshrc 2>/dev/null; then
        echo 'export PATH="$HOME/q/bin:$PATH"' >> ~/.zshrc
    fi
fi

q --version || true

# Use echo to pipe prompt to q chat
echo '{escaped_prompt}' | q chat {flags_str}
""".strip()

    return script


def get_tool_script(
    tool: Literal["cursor-agent", "copilot", "amazon-q"],
    prompt: str,
    command: str = "agent",
    model: Optional[str] = None,
    allow_all_tools: bool = True,
    accept_all: bool = True,
    no_interactive: bool = True
) -> str:
    """Get bash script for specified AI coding tool.

    Args:
        tool: Choose "cursor-agent", "copilot", or "amazon-q"
        prompt: The prompt to send
        command: Command for cursor-agent (default: "agent")
        model: Model for cursor-agent (e.g., "grok", "claude-sonnet-4")
        allow_all_tools: Auto-approve tools for copilot (default: True)
        accept_all: Auto-approve tools for Amazon Q (default: True)
        no_interactive: Non-interactive mode for Amazon Q (default: True)

    Returns:
        Complete bash script

    Raises:
        ValueError: If invalid tool specified
    """
    if tool == "cursor-agent":
        return generate_cursor_agent_script(prompt, command, model)
    elif tool == "copilot":
        return generate_copilot_script(prompt, allow_all_tools)
    elif tool == "amazon-q":
        return generate_amazon_q_script(prompt, accept_all, no_interactive)
    elif tool == "gemini":  
        return generate_gemini_cli_script(prompt, model, no_interactive)
    else:
        raise ValueError(f"Invalid tool: {tool}. Choose 'gemini', 'cursor-agent', 'copilot', or 'amazon-q'")

def generate_gemini_cli_script(prompt: str, model: Optional[str] = None, non_interactive: bool = True) -> str:
    """Generate bash script for Google Gemini CLI.

    Args:
        prompt: The prompt to send to Gemini CLI
        model: Model to use (e.g., "gemini-2.5-flash", "gemini-2.5-pro")
               Default is gemini-2.5-pro if not specified
        non_interactive: If True, run in non-interactive mode (exit after response)

    Returns:
        Complete bash script as string
    """

    # Escape single quotes in prompt for bash
    escaped_prompt = prompt.replace("'", "'\\''")
    
    # Build model flag
    model_flag = f"-m '{model}'" if model else ""
    
    script = f"""
set -e
# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
    echo "Node.js is required but not installed. Please install Node.js 20 or higher."
    exit 1
fi

# Check Node.js version (requires v20+)
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "Node.js version 20 or higher is required. Current version: $(node -v)"
    exit 1
fi

# Install Gemini CLI if not already installed
if ! command -v gemini >/dev/null 2>&1; then
    npm install -g @google/gemini-cli
fi

gemini --version || true

# Run Gemini CLI
if [ "{non_interactive}" = "True" ]; then
    # Non-interactive mode: pipe prompt and exit
    echo '{escaped_prompt}' | gemini --yolo
else
    # Interactive mode: use heredoc for multi-line prompt
    gemini --yolo <<'EOF'
{prompt}
/quit
EOF
fi
""".strip()
    
    return script


__all__ = [
    "generate_gemini_cli_script",
    "generate_cursor_agent_script",
    "generate_copilot_script",
    "generate_amazon_q_script",
    "get_tool_script"
]
