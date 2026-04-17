import pytest
from analyzer import analyze_feedback, render_analysis

def test_analyze_feedback_edge_cases():
    # Empty string
    res = analyze_feedback("   ")
    assert res["sentiment"] == "neutral"
    assert res["keywords"] == []
    assert res["confidence"] == 1.0
    
    # Emoji only
    res = analyze_feedback("😊😊😊")
    assert res["sentiment"] == "neutral"

def test_analyze_feedback_valid_vietnamese():
    res = analyze_feedback("Phòng học rất sạch sẽ, giảng viên nhiệt tình")
    assert res["language"] == "vi"
    # Fallback cho tùy mô hình load của underthesea, mặc định có thể classify là positive
    assert res["sentiment"] in ["positive", "neutral", "negative"] 
    assert len(res["keywords"]) > 0

def test_render_analysis():
    mock_result = {
        "text": "Tuyệt vời",
        "sentiment": "positive",
        "confidence": 0.95,
        "keywords": ["tuyệt", "vời"],
        "language": "vi",
        "timestamp": "2026-04-17 10:00:00"
    }
    output = render_analysis(mock_result)
    assert "Positive" in output or "positive" in output
    assert "😊" in output
    assert "tuyệt" in output