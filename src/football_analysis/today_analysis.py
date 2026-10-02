"""
今日比赛一键分析入口

功能：
1. 自动读取 data/api_football/fixtures_YYYY-MM-DD.json
2. 标准化 API-Football 比赛数据
3. 输出今日比赛清单
4. 不修改原始 API 数据
5. 数据不足时明确标记，不强行预测

后续可继续扩展：
- 历史 CSV 相似盘型
- 历史同赔
- 赔率变盘
- 泊松模型
- 数据异动
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_DATA_DIR = PROJECT_ROOT / "data" / "api_football"


def singapore_today() -> str:
    """返回新加坡当天日期 YYYY-MM-DD。"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d")


def find_today_file(date_str: Optional[str] = None) -> Path:
    """查找当天 API-Football fixture 文件。"""
    date_str = date_str or singapore_today()
    filename = f"fixtures_{date_str}.json"
    path = API_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"找不到今日比赛数据：{path}\n"
            f"请先运行 Football API Auto Fetch。"
        )

    return path


def load_fixture_json(path: Path) -> Dict[str, Any]:
    """读取 API-Football JSON。"""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("API 数据格式错误：根节点不是 JSON object。")

    return data


def normalize_fixture(item: Dict[str, Any]) -> Dict[str, Any]:
    """将 API-Football fixture 转换成统一格式。"""
    fixture = item.get("fixture") or {}
    league = item.get("league") or {}
    teams = item.get("teams") or {}
    goals = item.get("goals") or {}

    home = teams.get("home") or {}
    away = teams.get("away") or {}
    status = fixture.get("status") or {}

    return {
        "fixture_id": fixture.get("id"),
        "date": fixture.get("date"),
        "timestamp": fixture.get("timestamp"),
        "status": status.get("short"),
        "status_long": status.get("long"),
        "league_id": league.get("id"),
        "league": league.get("name"),
        "country": league.get("country"),
        "season": league.get("season"),
        "round": league.get("round"),
        "home_team_id": home.get("id"),
        "home_team": home.get("name"),
        "away_team_id": away.get("id"),
        "away_team": away.get("name"),
        "home_winner": home.get("winner"),
        "away_winner": away.get("winner"),
        "home_goals": goals.get("home"),
        "away_goals": goals.get("away"),
    }


def load_today_matches(date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """读取并标准化当天所有比赛。"""
    path = find_today_file(date_str)
    data = load_fixture_json(path)

    response = data.get("response")
    if not isinstance(response, list):
        raise ValueError("API 数据中没有找到 response 比赛列表。")

    matches: List[Dict[str, Any]] = []
    for item in response:
        if not isinstance(item, dict):
            continue

        match = normalize_fixture(item)
        if match["fixture_id"] is not None:
            matches.append(match)

    return matches


def build_analysis(match: Dict[str, Any]) -> Dict[str, Any]:
    """
    第一阶段只做数据完整性判断。
    不在数据不足时强行给出投注结论。
    """
    missing = []
    required_fields = [
        "fixture_id",
        "date",
        "league",
        "home_team",
        "away_team",
    ]

    for field in required_fields:
        value = match.get(field)
        if value is None or value == "":
            missing.append(field)

    evidence = "insufficient" if missing else "basic"

    return {
        "fixture_id": match.get("fixture_id"),
        "league": match.get("league"),
        "country": match.get("country"),
        "home_team": match.get("home_team"),
        "away_team": match.get("away_team"),
        "date": match.get("date"),
        "status": match.get("status"),
        "evidence_level": evidence,
        "missing_fields": missing,
        "recommendation": "暂不推荐",
        "reason": (
            "第一阶段只验证比赛数据，不强行生成投注结论。"
            if evidence == "basic"
            else "基础比赛字段不完整，证据不足。"
        ),
    }


def analyze_today(date_str: Optional[str] = None) -> Dict[str, Any]:
    """一键分析当天比赛。"""
    date_str = date_str or singapore_today()
    matches = load_today_matches(date_str)
    analyses = [build_analysis(match) for match in matches]

    return {
        "date": date_str,
        "source": "API-Football",
        "data_file": f"fixtures_{date_str}.json",
        "match_count": len(analyses),
        "matches": analyses,
    }


def print_report(report: Dict[str, Any]) -> None:
    """在终端输出简洁报告。"""
    print("=" * 70)
    print("足球今日比赛数据分析")
    print("=" * 70)

    print(f"日期：{report['date']}")
    print(f"数据源：{report['source']}")
    print(f"比赛数量：{report['match_count']}")
    print()

    for index, match in enumerate(report["matches"], start=1):
        print(f"{index:02d}. {match['home_team']} vs {match['away_team']}")
        print(f"    联赛：{match['league']}")
        print(f"    国家：{match['country']}")
        print(f"    状态：{match['status']}")
        print(f"    证据：{match['evidence_level']}")
        print(f"    当前结论：{match['recommendation']}")
        print(f"    说明：{match['reason']}")
        print("-" * 70)


def main() -> None:
    report = analyze_today()
    print_report(report)


if __name__ == "__main__":
    main()
