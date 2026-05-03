import pandas as pd
from timetable.grid import build_grid


def _make_df(rows):
    return pd.DataFrame(rows)


def test_empty_df_returns_html_table():
    df = _make_df([])
    html = build_grid(df)
    assert "<table" in html
    assert "월" in html
    assert "1교시" in html


def test_course_appears_in_correct_cell():
    df = _make_df([{
        "과목명": "신약개론",
        "교수명": "홍길동",
        "배정강의실": "A101",
        "요일": "월",
        "교시": "1-2",
        "학과": "신학대학원",
        "전공": "신학과",
    }])
    html = build_grid(df)
    assert "신약개론" in html
    assert "홍길동" in html
    assert "A101" in html


def test_online_course_included():
    df = _make_df([{
        "과목명": "온라인강의",
        "교수명": "박교수",
        "배정강의실": "온라인",
        "요일": "화",
        "교시": "3",
        "학과": "신학대학원",
        "전공": "신학과",
    }])
    html = build_grid(df)
    assert "온라인강의" in html


def test_unassigned_course_excluded():
    df = _make_df([{
        "과목명": "미배정과목",
        "교수명": "김교수",
        "배정강의실": "미배정-검토필요",
        "요일": "월",
        "교시": "1",
        "학과": "신학대학원",
        "전공": "신학과",
    }])
    html = build_grid(df)
    # unassigned courses should not appear in the grid cells
    assert "미배정과목" not in html
