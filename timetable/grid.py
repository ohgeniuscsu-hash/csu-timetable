import pandas as pd
from timetable.parser import parse_period

DAYS = ["월", "화", "수", "목", "금", "토"]
TIME_SLOTS = [
    (1,  "09:00~09:50"),
    (2,  "09:55~10:45"),
    (3,  "10:50~11:40"),
    (4,  "11:45~12:35"),
    (5,  "12:40~13:30"),
    (6,  "13:35~14:25"),
    (7,  "14:30~15:20"),
    (8,  "15:25~16:15"),
    (9,  "16:20~17:10"),
    (10, "17:15~18:05"),
    (11, "18:10~19:00"),
    (12, "19:05~19:55"),
    (13, "20:00~20:50"),
    (14, "20:55~21:45"),
    (15, "21:50~22:40"),
]


def _is_excluded(room: str) -> bool:
    return "검토필요" in room


def build_grid(df: pd.DataFrame) -> str:
    """Build an HTML timetable grid from a courses DataFrame.

    Rows are 1~15교시, columns are 월~토.
    Courses with 검토필요 rooms are excluded.
    Online courses (배정강의실 == '온라인') shown in blue italic.
    """
    cells: dict[int, dict[str, list[str]]] = {
        p: {d: [] for d in DAYS} for p, _ in TIME_SLOTS
    }

    for _, row in df.iterrows():
        room = str(row.get("배정강의실", "")).strip()
        if _is_excluded(room):
            continue
        day = str(row.get("요일", "")).strip()
        if day not in DAYS:
            continue
        period_str = str(row.get("교시", "")).strip()
        try:
            periods = parse_period(period_str)
        except ValueError:
            continue
        name = str(row.get("과목명", "")).strip()
        prof = str(row.get("교수명", "")).strip()
        room_label = room if room else "미정"
        if room == "온라인":
            content = (
                f"<em style='color:#4A7DC1'>{name}</em>"
                f"<br><small>{prof}</small>"
                f"<br><small style='color:#4A7DC1'>온라인</small>"
            )
        else:
            content = (
                f"{name}"
                f"<br><small>{prof}</small>"
                f"<br><small style='color:#4A7DC1'>{room_label}</small>"
            )
        for p in periods:
            if p in cells and day in cells[p]:
                cells[p][day].append(content)

    header_cells = "".join(
        f"<th style='background:#1A2C5E;color:#fff;padding:8px 12px;min-width:100px'>{d}</th>"
        for d in DAYS
    )
    header_row = (
        "<tr>"
        "<th style='background:#1A2C5E;color:#fff;padding:8px 12px;min-width:120px'>교시</th>"
        f"{header_cells}</tr>"
    )

    body_rows = []
    for period, time_label in TIME_SLOTS:
        period_label = (
            f"<b>{period}교시</b>"
            f"<br><small style='color:#888'>{time_label}</small>"
        )
        day_cells = ""
        for day in DAYS:
            contents = cells[period][day]
            if contents:
                inner = "<hr style='margin:4px 0;border-color:#eee'>".join(contents)
                day_cells += (
                    f"<td style='padding:8px;vertical-align:top;"
                    f"border:1px solid #E0E8F0'>{inner}</td>"
                )
            else:
                day_cells += "<td style='padding:8px;border:1px solid #E0E8F0'></td>"
        row_bg = "#F8FAFF" if period % 2 == 0 else "#FFFFFF"
        body_rows.append(
            f"<tr style='background:{row_bg}'>"
            f"<td style='padding:8px;background:#F0F4FA;border:1px solid #E0E8F0;"
            f"white-space:nowrap'>{period_label}</td>"
            f"{day_cells}</tr>"
        )

    body = "".join(body_rows)
    return (
        "<div style='overflow-x:auto'>"
        "<table style='border-collapse:collapse;width:100%;font-size:13px;"
        "font-family:sans-serif'>"
        f"<thead>{header_row}</thead>"
        f"<tbody>{body}</tbody>"
        "</table></div>"
    )
