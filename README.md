# Trading Analytics & Strategy Optimization Tool

Automates TradingView strategy backtests, parses exported data, analyzes performance, iteratively optimizes strategy code via LMM/embeddings, and produces human‑readable & structured reports.

---
## ✨ Key Features
- **Automated TradingView control** (login, script injection, date range, strategy tester) via Playwright in `automation/tradingview_bot.py`.
- **Parallel multi‑process optimization**: spins up multiple Chromium pages (`PROCESS_COUNT`) running independent optimization loops.
- **Adaptive optimization loop** (`optimise.py`): generates revised Pine Script using embeddings (`train/embedding.py`) until target criteria are met.
- **Result caching & merging** with JSON caches per process/condition (`utils/report_exporter.py`).
- **Analytics pipeline** (`analytics/strategy_analyzer.py`): aggregates metrics, tags run quality (GOOD / NORMAL / RISK / OVERFIT).
- **Report export**: TXT + XLSX (summary / detailed) plus persistent cache snapshots.
- **Config manager** (`utils/config_manager.py`): structured overrides & runtime mutation of `config.py` values.
- **Clipboard helpers & GitHub auto-commit** (`utils/clipboard_utils.py`, `utils/github_utils.py`).
- **Live progress display** using `utils/process_logger.py`.

---
## 📁 Project Structure (Core)
```
config.py                 # Global runtime configuration
m.py                      # Unified CLI entrypoint (evaluate / optimize)
optimise.py               # Async optimization agent (parallel pages)
evaluate.py               # One‑off evaluation & report export
train/
  embedding.py            # Embedding + LMM driven strategy code generation
  dev.pine                # Base PineScript template / fallback
  pc_*.pine               # Per-process evolving Pine scripts
src/
  automation/tradingview_bot.py
  analytics/strategy_analyzer.py
  utils/
    config_manager.py
    report_exporter.py
    excel_reader.py
    lmm_utils.py
    process_logger.py
    github_utils.py
    clipboard_utils.py
    file_operations.py
    signal_processing.py

data/
  sheets/                 # Raw downloaded TradingView XLSX files
  reports/                # Human readable exports (TXT/XLSX)
  cache/                  # Persistent merged JSON caches
```
A historical duplicate lives under `tdv-tool/`; prefer root-level files.

---
## 🧰 Requirements
- Python 3.10+
- Chromium (installed by Playwright)
- Dependencies in `requirements.txt`

### Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```
(Optional) To keep Playwright browsers up to date:
```bash
playwright install --with-deps chromium
```

---
## ⚙️ Configuration (`config.py`)
Key fields (names may vary; adjust to match your file):
- `TRADINGVIEW_USER`, `TRADINGVIEW_PASS`, `TRADINGVIEW_2FA_SECRET`
- `ASSET_NAME`, `TIME_BACKTEST`
- `TOTAL_CONDITIONS` (list of condition/ensemble IDs, e.g. `["1","2"]`)
- `TARGET_CRITERIA` (e.g. `total_trades_min`, `max_drawdown_max`)
- `TARGET_POTENTIAL`
- `MAX_ITERATIONS`, `MAX_CONSECUTIVE_ERRORS`, `MAX_DUPLICATE_CONSECUTIVE_ERRORS`
- `PROCESS_COUNT`
- `TOOL` (model/tool selector passed into embeddings)

Runtime overrides are exposed in `m.py` CLI flags.

---
## 🚀 Usage
The primary interface is `m.py`.

### 1. Evaluate (Download + Analyze + Export)
Runs initial/global test and optional per-condition strategy tests.
```bash
python m.py evaluate \
  --strategy btc-long \
  --conditions "1,3,5"        # Comma list

# Ranges allowed
python m.py evaluate --strategy xau-long --conditions "1-10"
```
If no new data can be fetched but a cache exists, reports are generated from cache.

### 2. Optimize (Iterative Strategy Improvement)
Performs iterative code generation + backtest until target criteria or iteration/error limits.
```bash
python m.py optimize \
  --strategy btc-long \
  --conditions "1" \
  --max-iterations 40 \
  --min-trades 250 \
  --max-drawdown 15
```
Internally calls `optimise.run_strategy_agent()` which:
1. Launches persistent Chromium context (`chrome_data_open/`).
2. For each process page: loads/creates `train/pc_<n>.pine` (copies `dev.pine` if empty).
3. Executes backtest, evaluates metrics vs targets.
4. Calls `run_strategy_embedding(..., model="auto")` to produce revised Pine code.
5. Applies script & re-runs backtest, updating cache & live logger.
6. Stops when targets met, max iterations, or error thresholds exceeded.

### 3. Helpful Flags (check `m.py` for exact names)
- `--process-count N` (parallel pages)
- `--max-iterations N`
- `--conditions "list"` / range
- `--min-trades N` (maps to `TARGET_CRITERIA.total_trades_min`)
- `--max-drawdown X` (maps to `TARGET_CRITERIA.max_drawdown_max`)
- `--tool NAME` (embedding / model tool chain)

---
## 🧪 Embedding & LMM Loop
File: `train/embedding.py`
- Consumes previous run metrics: net profit %, max drawdown %, total trades, percent profitable.
- Builds prompt + context from last assistant output (`assitent_comment_before`).
- Writes updated PineScript to the target `pinescript_path`.
- `model="auto"` indicates automatic model selection (implementation dependent—extend `embedding.py` to map this to an actual provider/model ID).

Extend by adding model routing logic for `auto` and integrating additional evaluation heuristics.

---
## 📤 Outputs
Location summary:
- Raw XLSX: `data/sheets/`
- Reports: `data/reports/<strategy>_<timestamp>.txt|.xlsx`
- Caches: `data/cache/*.json`
- Pine scripts evolving per process: `train/pc_*.pine`

Each run merges new metrics into the existing cache (see `ReportExporter._merge_with_cache`).

---
## 🔄 Git & Automation
`utils/github_utils.auto_commit_and_push()` can auto-commit changes (e.g., updated Pine scripts, cache snapshots). Ensure you have git remotes configured & auth ready.

---
## 🩺 Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Login hangs | Bad credentials / 2FA | Recheck `config.py` values |
| No XLSX downloaded | TradingView layout not loaded | Ensure strategy script added; check `action_setup_strategy` flow |
| Metrics not updating | Script code unchanged / cache reuse | Confirm new Pine code wrote; inspect `train/pc_<n>.pine` |
| Duplicate consecutive errors reset triggers often | Embedding producing identical code | Enhance diversity logic in `embedding.py` |
| Playwright errors about browser | Missing install | Run `playwright install chromium` |

---
## 🔧 Extending
Ideas:
- Add unit tests for analyzer & exporter logic in `test/`.
- Implement advanced selection for `model="auto"` (latency/quality scoring).
- Add risk-adjusted metrics (Sharpe, SQN) to analyzer.
- Introduce YAML config alternative.
- Persist run timeline (iterations) as a time series CSV.

---
## 🛡️ Safety & Rate Limits
Automating TradingView may be subject to ToS; ensure compliance. Space out iterations (`slow_mo`, sleeps) to reduce flagging risk.

---
## ✅ Quick Start Recap
```bash
# 1. Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. Configure
vim config.py   # Set credentials, targets, conditions

# 3. Evaluate
python m.py evaluate --strategy btc-long --conditions "1-3"

# 4. Optimize
python m.py optimize --strategy btc-long --conditions "1" --max-iterations 30
```

---
## 📄 License
Add a LICENSE file (MIT recommended) if you intend to distribute.

---
## 🙌 Contributing
PRs welcome: please include concise descriptions, keep functions small, and add/adjust docs when behavior changes.

---
Happy optimizing! 🧠📈
