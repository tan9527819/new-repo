"""
简单的 API-Football HTTP 客户端实现。
- 从环境变量读取 API key
- 支持自定义 base_url
- 简单重试、超时与错误处理
"""

import os
import time
import logging
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)


class APIError(Exception):
    pass


class APIFootballClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key or os.getenv('API_FOOTBALL_KEY')
        if not self.api_key:
            raise RuntimeError('API_FOOTBALL_KEY is required in the environment')
        self.base_url = base_url or os.getenv('API_FOOTBALL_BASE_URL', 'https://v3.football.api-sports.io')
        self.session = requests.Session()
        self.session.headers.update({
            'x-apisports-key': self.api_key,
            'Accept': 'application/json',
        })
        self.timeout = timeout

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, retries: int = 2):
        url = self.base_url.rstrip('/') + '/' + path.lstrip('/')
        attempt = 0
        while True:
            try:
                logger.debug('API request %s %s (attempt %s)', method, url, attempt + 1)
                resp = self.session.request(method, url, params=params, json=json, timeout=self.timeout)
                if resp.status_code >= 500 and attempt < retries:
                    attempt += 1
                    time.sleep(1 + attempt)
                    continue
                if not resp.ok:
                    raise APIError(f'API request failed: {resp.status_code} {resp.text}')
                return resp.json()
            except requests.Timeout:
                if attempt < retries:
                    attempt += 1
                    logger.warning('Request timeout, retrying... (%s/%s)', attempt, retries)
                    time.sleep(0.5 * attempt)
                    continue
                raise
            except requests.RequestException as e:
                raise APIError(str(e))

    # convenience wrappers
    def get(self, path: str, params: Optional[Dict[str, Any]] = None):
        return self._request('GET', path, params=params)


