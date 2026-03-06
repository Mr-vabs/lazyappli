import pytest
from src.parser import parse_resume

def test_parse_resume_not_found():
    with pytest.raises(FileNotFoundError):
        parse_resume("nonexistent.pdf")

def test_parse_resume_wrong_extension():
    with pytest.raises(ValueError):
        parse_resume("fake_resume.docx")
