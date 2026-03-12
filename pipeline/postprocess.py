# postprocess.py
# 对模型原始输出进行清洗、修正和兜底处理
# 保证下游使用的数据结构稳定可靠
# 不负责模型调用，不参与流程控制

import re
_OUTPUT_RE = re.compile(r"<OUTPUT>(.*?)</OUTPUT>", re.DOTALL)
def extract_output(raw: str) -> str:
    """
    Extract the content inside <OUTPUT>...</OUTPUT>.
    Enforce: nothing outside tags (ignoring surrounding whitespace).
    """
    if raw is None:
        raise ValueError("Model output is None")

    m = _OUTPUT_RE.search(raw)
    if not m:
        raise ValueError("Missing <OUTPUT>...</OUTPUT> wrapper")

    inside = m.group(1).strip()

    # Enforce no extra text outside tags (allow whitespace)
    cleaned = raw.strip()
    expected = f"<OUTPUT>{m.group(1)}</OUTPUT>".strip()
    if cleaned != expected:
        # Some models add newlines around tags; allow a softer check:
        # remove surrounding whitespace and compare after normalizing
        norm_cleaned = re.sub(r"\s+", " ", cleaned)
        norm_expected = re.sub(r"\s+", " ", expected)
        if norm_cleaned != norm_expected:
            raise ValueError("Found extra text outside <OUTPUT> tags")

    if not inside:
        raise ValueError("Empty output inside <OUTPUT> tags")

    return inside
def postprocess_bullets(raw: str) -> list[str]:
    text = extract_output(raw)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) != 5:
        raise ValueError(f"Expected 5 bullet lines, got {len(lines)}")
    return lines
