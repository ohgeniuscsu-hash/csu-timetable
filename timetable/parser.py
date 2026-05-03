import re


def parse_period(period_str: str) -> set[int]:
    s = str(period_str).strip()
    single = re.fullmatch(r'(\d+)', s)
    if single:
        return {int(single.group(1))}
    range_match = re.search(r'(\d+)\s*[~\-]\s*(\d+)', s)
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        return set(range(start, end + 1))
    raise ValueError(f"교시 형식 오류: '{period_str}'")
