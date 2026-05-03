import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


def _make_client(semester_rows, run_rows):
    client = MagicMock()
    # list_semesters query chain
    sem_chain = (
        client.table.return_value
        .select.return_value
        .order.return_value
    )
    sem_chain.execute.return_value.data = semester_rows

    # get_latest_run query chain
    run_chain = (
        client.table.return_value
        .select.return_value
        .eq.return_value
        .order.return_value
        .limit.return_value
    )
    run_chain.execute.return_value.data = run_rows
    return client


@patch("timetable.db.get_client")
def test_list_semesters_deduped(mock_gc):
    client = _make_client(
        [{"semester": "2025-2학기"}, {"semester": "2025-2학기"}, {"semester": "2025-1학기"}],
        [],
    )
    mock_gc.return_value = client
    from timetable.db import list_semesters
    result = list_semesters(client=client)
    assert result == ["2025-2학기", "2025-1학기"]


@patch("timetable.db.get_client")
def test_get_latest_run_returns_none_when_empty(mock_gc):
    client = _make_client([], [])
    mock_gc.return_value = client
    from timetable.db import get_latest_run
    result = get_latest_run("2025-2학기", client=client)
    assert result is None


@patch("timetable.db.get_client")
def test_get_latest_run_returns_dataframe(mock_gc):
    records = [{"과목명": "신약개론", "전공": "신학과", "학과": "신학대학원",
                "교수명": "홍길동", "요일": "월", "교시": "1-2", "배정강의실": "A101"}]
    run_rows = [{"result_json": records, "version": 3, "created_at": "2026-05-02T10:00:00"}]
    client = _make_client([], run_rows)
    mock_gc.return_value = client
    from timetable.db import get_latest_run
    result = get_latest_run("2026-1학기", client=client)
    assert result is not None
    assert isinstance(result["result_df"], pd.DataFrame)
    assert result["version"] == 3
    assert result["result_df"].iloc[0]["과목명"] == "신약개론"
