import re


def parse_period(period_str: str) -> set[int]:
    """Convert Korean class period string to a set of period numbers.

    Accepts "3" (single), "3-5" or "3~5" (range), with optional spaces.
    Reversed ranges (e.g. "5-3") are normalized to ascending order.
    Raises ValueError for unrecognized formats.
    """
    s = str(period_str).strip()
    single = re.fullmatch(r'(\d+)', s)
    if single:
        return {int(single.group(1))}
    range_match = re.fullmatch(r'(\d+)\s*[-~]\s*(\d+)', s)
    if range_match:
        a, b = int(range_match.group(1)), int(range_match.group(2))
        start, end = min(a, b), max(a, b)
        return set(range(start, end + 1))
    raise ValueError(f"교시 형식 오류: '{period_str}'")
