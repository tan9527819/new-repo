"""
简单的本地缓存，基于 JSON 文件存储。
缓存 key 以 fixture_{id}.json 保存在 data/raw/cache
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

CACHE_DIR = Path('data/raw/cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_TTL = int(os.getenv('API_CACHE_TTL_SECONDS', '3600'))


def _cache_path(key: str) -> Path:
    safe = key.replace('/', '_')
    return CACHE_DIR / f"{safe}.json"


def set_cache(key: str, data: dict):
    p = _cache_path(key)
    payload = {
        'timestamp': datetime.utcnow().isoformat(),
        'data': data,
    }
    with p.open('w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)


def get_cache(key: str) -> Optional[dict]:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        with p.open('r', encoding='utf-8') as f:
            payload = json.load(f)
        ts = datetime.fromisoformat(payload.get('timestamp'))
        if datetime.utcnow() - ts > timedelta(seconds=CACHE_TTL):
            return None
        return payload.get('data')
    except Exception:
        return None
