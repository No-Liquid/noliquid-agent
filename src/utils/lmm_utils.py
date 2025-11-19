
import json
import os
from typing import Any
from datetime import datetime

CACHE_PATH = os.environ.get("CACHE_PATH", "data/prompts/potential_conditions.json")


def decode_LMM_output(output: str) -> dict[str, Any]:
    """Decode the output of the LMM."""
    return {
        "assistant": output,
        "user": "",
        "last_code": "",
        "change": ""
    }
    # outputs = output.split("\n")
    # text_user = ""
    # text_assistant = ""
    # change: list[dict[str, str]] = []
    # last_code = ""
    # for o in outputs:
    #     try:
    #         o = json.loads(o)
    #         if o.get("type") == "user":
    #             text_user += o["message"]["content"][0]["text"]
    #         elif o.get("type") == "result":
    #             text_assistant += o["result"]
    #         elif o.get("type") == "tool_call" and o.get("subtype") == "completed":
    #             new_text = o["tool_call"]["editToolCall"]["args"]["strReplace"]["newText"]
    #             old_text = o["tool_call"]["editToolCall"]["args"]["strReplace"]["oldText"]

    #             if new_text not in [c["new"] for c in change]:
    #                 change.append({"old": old_text, "new": new_text})
    #     except Exception:
    #         continue

    # if "```pinescript" in text_assistant:
    #     last_code = text_assistant.split("```pinescript")[1].split("```")[0].replace("\n", "")
    # else:
    #     last_code = text_assistant
    # if text_assistant == "":
    #     text_assistant = output
    # return {
    #     "user": text_user,
    #     "change": change,
    #     "last_code": last_code,
    #     "assistant": text_assistant,
    # }


def ensure_cache_file(cache_path: str = CACHE_PATH) -> None:
    """Make sure the cache file exists and is a valid JSON dict."""
    if not os.path.exists(cache_path):
        print(cache_path)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({}, f)  # empty dict, not list


def get_cache(cache_path: str = CACHE_PATH) -> dict[str, Any]:
    """Get cache as a dict."""
    ensure_cache_file(cache_path)
    with open(cache_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def add_to_cache(change: dict[str, Any], cache_path: str = CACHE_PATH) -> None:
    """Add to cache with timestamp as key."""
    cache = get_cache(cache_path)
    now = datetime.now().isoformat()
    cache[now] = change
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    with open("data/prompts/BTC (Bitoin)-2025-09-26 17:48:15.300003.txt", "r", encoding="utf-8") as f:
        output = f.read()
    res = decode_LMM_output(output)
    add_to_cache({"change": res["change"], "last_code": res["last_code"]}, "data/prompts/abc.json")


__all__ = ["decode_LMM_output", "add_to_cache"]