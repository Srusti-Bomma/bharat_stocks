from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

# Load NSE working stocks metadata once and expose helpers for lookups.

_META_BY_SYMBOL: Dict[str, Dict] = {}
_META_BY_NAME: Dict[str, Dict] = {}

try:
    # Go up to project root (D:\stocks) and then to nse_working_stocks.json
    # symbol_meta.py lives in backend/app/, so parents[2] == project root.
    meta_path = Path(__file__).resolve().parents[2] / "nse_working_stocks.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    if item.get("symbol"):
                        _META_BY_SYMBOL[item["symbol"].upper()] = item
                    if item.get("name"):
                        # Normalize name for easier matching (lowercase, stripped)
                        norm_name = item["name"].lower().strip()
                        _META_BY_NAME[norm_name] = item
except Exception:
    # On any error, just leave the cache empty; callers will handle None.
    _META_BY_SYMBOL = {}
    _META_BY_NAME = {}


def get_sector_for_symbol(symbol: str, company_name: str = None) -> Optional[str]:
    """Return sector name for the given NSE symbol using local metadata.

    Strategies:
    1. Exact symbol match.
    2. Symbol match with .NS/.BSE stripped.
    3. Exact company name match (if provided).
    """
    if not symbol:
        return None
    
    # 1. Exact symbol match
    sym_upper = symbol.upper().strip()
    data = _META_BY_SYMBOL.get(sym_upper)
    if isinstance(data, dict):
        return data.get("sector")
    
    # 2. Strip suffixes
    for suffix in [".NS", ".BSE"]:
        if sym_upper.endswith(suffix):
            stripped = sym_upper[:-len(suffix)]
            data = _META_BY_SYMBOL.get(stripped)
            if isinstance(data, dict):
                return data.get("sector")
    
    # 3. Company name match
    if company_name:
        norm_input_name = company_name.lower().strip()
        data = _META_BY_NAME.get(norm_input_name)
        if isinstance(data, dict):
            return data.get("sector")
            
    return None
