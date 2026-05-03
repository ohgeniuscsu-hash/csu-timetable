import pandas as pd
import streamlit as st
from supabase import create_client, Client


def get_client() -> Client:
    cfg = st.secrets["supabase"]
    return create_client(cfg["url"], cfg["key"])


def list_semesters(*, client: Client = None) -> list[str]:
    if client is None:
        client = get_client()
    res = (
        client.table("assignment_runs")
        .select("semester")
        .order("created_at", desc=True)
        .execute()
    )
    seen: list[str] = []
    for row in res.data:
        if row["semester"] not in seen:
            seen.append(row["semester"])
    return seen


def list_run_history(*, client: Client = None) -> list[dict]:
    """학기별 최신 버전 정보를 반환. [{semester, version, created_at}] 최신순."""
    if client is None:
        client = get_client()
    res = (
        client.table("assignment_runs")
        .select("semester,version,created_at")
        .order("created_at", desc=True)
        .execute()
    )
    seen: dict[str, dict] = {}
    for row in res.data:
        s = row["semester"]
        if s not in seen:
            seen[s] = {"semester": s, "version": row["version"], "created_at": row["created_at"]}
    return list(seen.values())


def get_latest_run(semester: str, *, client: Client = None) -> dict | None:
    if client is None:
        client = get_client()
    res = (
        client.table("assignment_runs")
        .select("*")
        .eq("semester", semester)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    if not res.data:
        return None
    row = res.data[0]
    return {
        "result_df": pd.DataFrame(row["result_json"]),
        "version": row["version"],
        "created_at": row["created_at"],
    }
