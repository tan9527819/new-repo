# tests for report
from football_analysis.analysis.report import generate_report

def test_report_structure():
    rpt = generate_report({'p':1},{},[],{}, {'sample_size':10}, {'missing_home':0})
    assert 'evidence_level' in rpt
    assert 'conclusion' in rpt
