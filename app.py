import base64
from pathlib import Path

import streamlit as st

from timetable.db import list_semesters, get_latest_run, list_run_history
from timetable.grid import build_grid


def _logo_b64() -> str:
    p = Path(__file__).parent / "csu_seal.png"
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


st.set_page_config(
    page_title="총신대학교 대학원 시간표",
    page_icon="🎓",
    layout="wide",
)

logo = _logo_b64()
logo_tag = (
    f'<img src="data:image/png;base64,{logo}" '
    f'style="height:48px;border-radius:50%;flex-shrink:0;">'
    if logo else ""
)

st.markdown(f"""
<style>
  /* ── Streamlit 기본 UI 제거 ── */
  header[data-testid="stHeader"] {{ display: none !important; }}
  [data-testid="stToolbar"] {{ display: none !important; }}
  footer[data-testid="stFooter"] {{ display: none !important; }}
  #MainMenu {{ display: none !important; }}

  /* ── 레이아웃 ── */
  .block-container {{ padding-top: 0 !important; }}
  .stApp {{ background-color: #F0F4FA; }}

  /* ── 본문 텍스트 ── */
  [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] li,
  [data-testid="stMarkdownContainer"] span,
  .stApp label,
  .stApp .stCaption p,
  .stApp .stCaption span {{
      color: #1A2C5E !important;
  }}
  h1, h2, h3, h4, h5, h6 {{ color: #1A2C5E !important; }}

  /* ── 네이비 헤더 내부는 항상 흰색 (ID 특이도로 위 규칙 덮어씀) ── */
  #csu-header, #csu-header * {{ color: #FFFFFF !important; }}

  /* ── 셀렉트박스 ── */
  .stSelectbox label {{ color: #1A2C5E !important; font-weight: 600 !important; }}
  .stSelectbox [data-baseweb="select"] > div {{
      background-color: #FFFFFF !important;
      color: #1A2C5E !important;
  }}

  /* ── 탭 ── */
  .stTabs [data-baseweb="tab-list"] {{
      background-color: #FFFFFF;
      border-radius: 8px;
      padding: 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
      color: #6B80A0 !important;
      font-weight: 500;
  }}
  .stTabs [data-baseweb="tab"] p,
  .stTabs [data-baseweb="tab"] div {{
      color: #6B80A0 !important;
  }}
  .stTabs [data-baseweb="tab"][aria-selected="true"] {{
      color: #1A2C5E !important;
      font-weight: 700;
      border-bottom: 3px solid #F0C040;
  }}
  .stTabs [data-baseweb="tab"][aria-selected="true"] p,
  .stTabs [data-baseweb="tab"][aria-selected="true"] div {{
      color: #1A2C5E !important;
  }}

  /* ── 캡션 ── */
  small, .stCaption {{ color: #5A6E8C !important; }}
</style>
<div id="csu-header" style="background:#1A2C5E;padding:14px 40px;display:flex;
            align-items:center;gap:16px;margin-bottom:28px;">
  {logo_tag}
  <span style="font-size:20px;font-weight:700;letter-spacing:-0.3px;">
    총신대학교 대학원&nbsp;&nbsp;시간표
  </span>
</div>
""", unsafe_allow_html=True)

# ── Load semester list ────────────────────────────────────────
try:
    semesters = list_semesters()
except Exception as e:
    st.error(f"데이터를 불러올 수 없습니다: {e}")
    st.stop()

if not semesters:
    st.info("아직 배정된 시간표가 없습니다.")
    st.stop()

tab1, tab2 = st.tabs(["📅 시간표", "📋 변경 이력"])

with tab1:
    # ── Controls ─────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 2])
    with ctrl1:
        selected_semester = st.selectbox("학기", semesters)

    # ── Fetch data ───────────────────────────────────────────
    run = get_latest_run(selected_semester)
    if run is None:
        st.info("선택한 학기의 데이터가 없습니다.")
        st.stop()

    df = run["result_df"]

    # ── Filters ──────────────────────────────────────────────
    all_schools = sorted(df["학과"].dropna().unique().tolist()) if "학과" in df.columns else []
    with ctrl2:
        school_options = ["전체"] + all_schools
        selected_school = st.selectbox("대학원", school_options)

    if selected_school != "전체":
        filtered_df = df[df["학과"] == selected_school]
    else:
        filtered_df = df

    all_majors = sorted(filtered_df["전공"].dropna().unique().tolist()) if "전공" in filtered_df.columns else []
    with ctrl3:
        major_options = ["전체"] + all_majors
        selected_major = st.selectbox("전공", major_options)

    if selected_major != "전체":
        filtered_df = filtered_df[filtered_df["전공"] == selected_major]

    # ── Render grid ──────────────────────────────────────────
    st.markdown("### 강의 시간표")

    if filtered_df.empty:
        st.info("해당 조건의 과목이 없습니다.")
    else:
        grid_html = build_grid(filtered_df)
        st.markdown(grid_html, unsafe_allow_html=True)

    # ── Footer ───────────────────────────────────────────────
    created = run["created_at"][:16].replace("T", " ")
    st.caption(f"마지막 업데이트: {created}  |  v{run['version']}  |  학기: {selected_semester}")

with tab2:
    st.markdown("### 📋 변경 이력")
    try:
        history = list_run_history()
    except Exception as e:
        st.error(f"데이터를 불러올 수 없습니다: {e}")
        history = []

    if not history:
        st.info("저장된 이력이 없습니다.")
    else:
        for item in history:
            created_str = item["created_at"][:16].replace("T", " ")
            st.markdown(
                f"""<div style="background:#FFFFFF;border-radius:10px;padding:14px 20px;
                    margin-bottom:10px;border-left:4px solid #F0C040;">
                  <span style="font-weight:700;font-size:16px;color:#1A2C5E !important;">
                    {item['semester']}
                  </span>
                  <span style="color:#5A6E8C !important;font-size:13px;margin-left:12px;">
                    v{item['version']} 기준 &nbsp;·&nbsp; 마지막 업데이트 {created_str}
                  </span>
                </div>""",
                unsafe_allow_html=True,
            )
