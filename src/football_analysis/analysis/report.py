"""
生成分析报告的简单模块。将统计与数据质量分区输出。
"""
from typing import Dict, Any, List


def evidence_level(sample_size: int, quality_issues: int) -> str:
    if sample_size < 5:
        return 'insufficient'
    if quality_issues > 0 and sample_size < 20:
        return 'weak'
    if sample_size < 50:
        return 'moderate'
    return 'strong'


def generate_report(market_data: Dict[str, Any], same_odds: List[Dict[str, Any]], similar: List[Dict[str, Any]], movements: Dict[str, Any], aggregates: Dict[str, Any], quality: Dict[str, Any]) -> Dict[str, Any]:
    sample_size = aggregates.get('sample_size', 0)
    q_issues = sum(1 for v in quality.values() if v)
    level = evidence_level(sample_size, q_issues)
    return {
        'market_data': market_data,
        'same_odds': same_odds,
        'similar': similar,
        'movements': movements,
        'aggregates': aggregates,
        'quality': quality,
        'evidence_level': level,
        'conclusion': 'evidence_insufficient' if level == 'insufficient' else 'evidence_present',
        'advice': 'No betting recommendations provided. Review evidence level and risk.'
    }
