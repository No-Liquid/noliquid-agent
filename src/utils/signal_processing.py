"""
Signal encoding and decoding utilities.
"""

from typing import Dict, Any


def encode_signals(signal: str) -> Dict[str, Any]:
    """
    Parse trading signal string into components.
    
    Args:
        signal: Signal string from TradingView
        
    Returns:
        Dictionary containing parsed signal components
    """
    parts = signal.split(" | ")
    
    if len(parts) < 3:
        # Handle incomplete signals
        return {
            "conditions": signal,
            "limit": 0.0,
            "sizeEquity": 0.0
        }
    
    return {
        "conditions": str(parts[0]).strip(),
        "limit": float(parts[1]) if parts[1].strip() else 0.0,
        "sizeEquity": float(parts[2]) if parts[2].strip() else 0.0
    }


def decode_signal(signal: str) -> tuple[str, str]:
    """
    Decode signal into condition and size components.
    
    Args:
        signal: Signal string
        
    Returns:
        Tuple of (conditions, size_str)
    """
    try:
        data = encode_signals(signal)
        conditions = str(data.get("conditions", "")).strip()
        size_equity = data.get("sizeEquity", 0.0)
        
        # Format size equity as percentage string
        size_str = ""
        if size_equity != 0.0:
            pct = float(size_equity) * 100.0
            if abs(pct - round(pct)) < 1e-9:
                size_str = str(int(round(pct)))
            else:
                size_str = f"{pct:.2f}".rstrip('0').rstrip('.')
        
        return conditions, size_str
    except Exception:
        return signal.strip(), ""
