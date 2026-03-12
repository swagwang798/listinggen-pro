# tests/test_postprocess.py
# 测试后处理函数的正确性
import pytest
from listinggen.pipeline.postprocess import extract_output, postprocess_bullets

def test_extract_output_basic():
    raw = "<OUTPUT>Hello</OUTPUT>"
    assert extract_output(raw) == "Hello"

def test_extract_output_reject_extra():
    raw = "Sure!\n<OUTPUT>Hello</OUTPUT>"
    with pytest.raises(ValueError):
        extract_output(raw)

def test_postprocess_bullets_exact_5_lines():
    raw = "<OUTPUT>\nA\nB\nC\nD\nE\n</OUTPUT>"
    assert postprocess_bullets(raw) == ["A","B","C","D","E"]

def test_postprocess_bullets_reject_wrong_count():
    raw = "<OUTPUT>\nA\nB\n</OUTPUT>"
    with pytest.raises(ValueError):
        postprocess_bullets(raw)
