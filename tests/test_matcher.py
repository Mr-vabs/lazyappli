import pytest
from src.matcher import calculate_match_score

def test_calculate_match_score_exact():
    resume = "Software Engineer python java"
    jd = "Software Engineer python java"
    score = calculate_match_score(resume, jd)
    assert score > 90.0

def test_calculate_match_score_partial():
    resume = "Python Developer with django experience"
    jd = "Software Engineer python java"
    score = calculate_match_score(resume, jd)
    assert 0.0 < score < 100.0

def test_calculate_match_score_no_match():
    resume = "Chef cooking food"
    jd = "Software Engineer python java"
    score = calculate_match_score(resume, jd)
    assert score == 0.0

def test_calculate_match_score_empty():
    assert calculate_match_score("", "test") == 0.0
    assert calculate_match_score("test", "") == 0.0
