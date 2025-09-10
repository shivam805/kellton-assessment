
from app.agent import analyze_text, modify_text

def test_analyze_basic():
    report = analyze_text("This are bad sentence. It was written by me.")
    assert "summary" in report and "violations" in report
    assert isinstance(report["violations"], list)

def test_modify_text():
    updated, changes = modify_text("He are good.", [])
    assert isinstance(updated, str)
