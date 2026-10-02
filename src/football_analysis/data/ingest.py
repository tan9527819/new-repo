"""
数据拉取与持久化模块（示例占位）。
实现目标：
- 从 API-Football 拉取比赛与盘口数据
- 将数据整理并追加到 CSV 历史赔率数据库

请在本文件中补全 API 调用与错误处理逻辑。
"""

import os
from pathlib import Path

API_KEY = os.getenv('API_FOOTBALL_KEY')
ODDS_DB_PATH = os.getenv('ODDS_DB_PATH', './data/odds_history.csv')


def fetch_matches(*, league_id=None, from_date=None, to_date=None):
    """示例：调用 API-Football 返回原始 JSON 数据（需补充实现）。"""
    raise NotImplementedError("请实现 fetch_matches 来调用 API-Football 并返回 JSON 数据")


def save_odds_to_csv(records, path=ODDS_DB_PATH):
    """将拉取到的赔率记录追加保存为 CSV。"""
    import pandas as pd
    p = Path(path)
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    if p.exists():
        df.to_csv(p, mode='a', header=False, index=False)
    else:
        df.to_csv(p, index=False)


if __name__ == '__main__':
    print('示例：请实现 fetch_matches 并调用 save_odds_to_csv')
