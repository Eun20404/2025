# Streamlit 독서 기록 & 분석 앱
# -------------------------------------------------
# 필요한 패키지
# pip install streamlit pandas requests wordcloud matplotlib pillow python-dateutil
# 실행: streamlit run streamlit_book_log_app.py
# -------------------------------------------------

from __future__ import annotations
import io
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, List, Optional

import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image

st.set_page_config(page_title="독서 기록 & 분석", page_icon="📚", layout="wide")

# -----------------------------
# 유틸
# -----------------------------

def _today_str():
    return datetime.today().strftime("%Y-%m-%d")

@st.cache_data(show_spinner=False)
def search_google_books(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": max_results}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    results = []
    for it in items:
        info = it.get("volumeInfo", {})
        ids = info.get("industryIdentifiers", [])
        isbn10 = next((i.get("identifier") for i in ids if i.get("type") == "ISBN_10"), None)
        isbn13 = next((i.get("identifier") for i in ids if i.get("type") == "ISBN_13"), None)
        image_links = info.get("imageLinks", {})
        results.append({
            "source": "GoogleBooks",
            "id": it.get("id"),
            "title": info.get("title"),
            "subtitle": info.get("subtitle"),
            "authors": ", ".join(info.get("authors", [])),
            "publisher": info.get("publisher"),
            "publishedDate": info.get("publishedDate"),
            "pageCount": info.get("pageCount"),
            "categories": ", ".join(info.get("categories", [])),
            "language": info.get("language"),
            "isbn_10": isbn10,
            "isbn_13": isbn13,
            "thumbnail": image_links.get("thumbnail") or image_links.get("smallThumbnail"),
            "infoLink": info.get("infoLink") or it.get("selfLink"),
        })
    return results

@st.cache_data(show_spinner=False)
def search_open_library(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    url = "https://openlibrary.org/search.json"
    params = {"q": query, "limit": limit}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    docs = data.get("docs", [])
    results = []
    for d in docs:
        cover_id = d.get("cover_i")
        isbn_list = d.get("isbn", [])
        isbn10 = next((i for i in isbn_list if len(i) == 10), None)
        isbn13 = next((i for i in isbn_list if len(i) == 13), None)
        categories = d.get("subject", [])
        results.append({
            "source": "OpenLibrary",
            "id": d.get("key"),
            "title": d.get("title"),
            "subtitle": None,
            "authors": ", ".join(d.get("author_name", []) or []),
            "publisher": ", ".join(d.get("publisher", [])[:1]) if d.get("publisher") else None,
            "publishedDate": str(d.get("first_publish_year")) if d.get("first_publish_year") else None,
            "pageCount": d.get("number_of_pages_median"),
            "categories": ", ".join(categories[:5]) if categories else None,
            "language": None,
            "isbn_10": isbn10,
            "isbn_13": isbn13,
            "thumbnail": f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None,
            "infoLink": f"https://openlibrary.org{d.get('key')}" if d.get("key") else None,
        })
    return results

# ISBN 단일 조회 (Google Books 우선)
@st.cache_data(show_spinner=False)
def lookup_by_isbn(isbn: str) -> List[Dict[str, Any]]:
    isbn = isbn.replace("-", " ").strip()
    # Try Google Books first
    google = search_google_books(f"isbn:{isbn}", max_results=1)
    if google:
        return google
    # Fallback to Open Library
    ol = search_open_library(f"isbn:{isbn}", limit=1)
    return ol

# 초기 세션 상태
if "library" not in st.session_state:
    st.session_state.library = pd.DataFrame(columns=[
        "title", "authors", "publisher", "publishedDate", "pageCount", "categories",
        "isbn_10", "isbn_13", "language", "infoLink", "thumbnail", "date_read", "notes", "source"
    ])

# -----------------------------
# 사이드바: 데이터 관리
# -----------------------------
with st.sidebar:
    st.header("⚙️ 데이터 관리")
    uploaded = st.file_uploader("CSV 불러오기", type=["csv"], help="이전에 저장한 독서 기록을 불러옵니다.")
    if uploaded is not None:
        try:
            df_new = pd.read_csv(uploaded)
            # 필요한 컬럼이 없으면 보강
            for col in st.session_state.library.columns:
                if col not in df_new.columns:
                    df_new[col] = None
            # 순서 맞추기
            df_new = df_new[st.session_state.library.columns]
            st.session_state.library = df_new
            st.success("CSV를 불러왔어요!")
        except Exception as e:
            st.error(f"불러오기 실패: {e}")

    if not st.session_state.library.empty:
        csv = st.session_state.library.to_csv(index=False).encode("utf-8-sig")
        st.download_button("💾 CSV로 내보내기", data=csv, file_name="reading_log.csv", mime="text/csv")

    st.markdown("---")
    st.caption("데이터는 브라우저 세션에 저장됩니다. 필요시 CSV로 저장해두세요.")

# -----------------------------
# 메인: 제목
# -----------------------------
st.title("📚 독서 기록 & 분석")
st.caption("Open Library / Google Books API로 메타데이터 자동 채우기 · 추이 그래프 · 장르 워드클라우드")

# -----------------------------
# 책 추가 섹션
# -----------------------------
st.subheader("➕ 책 추가하기")
col_api, col_query = st.columns([1, 3])
with col_api:
    api_choice = st.radio("검색 소스", ["Google Books", "Open Library", "ISBN"], horizontal=True)

with col_query:
    if api_choice == "ISBN":
        isbn_input = st.text_input("ISBN으로 추가", placeholder="예: 9788972756194")
        do_search = st.button("조회")
        if do_search and isbn_input:
            with st.spinner("ISBN 조회 중..."):
                results = lookup_by_isbn(isbn_input)
    else:
        query = st.text_input("제목/저자/키워드로 검색", placeholder="예: 하루키, 작은 아씨들, AI ethics")
        max_n = st.slider("검색 개수", 1, 20, 10)
        do_search = st.button("검색")
        results = []
        if do_search and query:
            with st.spinner("검색 중..."):
                if api_choice == "Google Books":
                    results = search_google_books(query, max_results=max_n)
                else:
                    results = search_open_library(query, limit=max_n)

if do_search:
    if results:
        st.success(f"{len(results)}건 찾았어요. 아래에서 선택해 추가하세요.")
        for i, r in enumerate(results):
            with st.expander(f"{i+1}. {r.get('title')} — {r.get('authors')}"):
                cols = st.columns([1,3])
                with cols[0]:
                    if r.get("thumbnail"):
                        try:
                            st.image(r["thumbnail"], use_container_width=True)
                        except Exception:
                            st.write(":grey[이미지 불가]")
                    else:
                        st.write(":grey[표지 이미지 없음]")
                with cols[1]:
                    meta_cols = {
                        "제목": r.get("title"),
                        "부제": r.get("subtitle"),
                        "저자": r.get("authors"),
                        "출판사": r.get("publisher"),
                        "출간": r.get("publishedDate"),
                        "쪽수": r.get("pageCount"),
                        "장르/카테고리": r.get("categories"),
                        "ISBN-10": r.get("isbn_10"),
                        "ISBN-13": r.get("isbn_13"),
                        "언어": r.get("language"),
                        "링크": r.get("infoLink"),
                        "출처": r.get("source"),
                    }
                    st.json({k: v for k, v in meta_cols.items() if v})

                    date_read = st.date_input("읽은 날짜", value=datetime.today())
                    notes = st.text_area("메모", placeholder="느낀 점, 인상 깊은 문장 등")
                    if st.button(f"이 책 추가하기 #{i+1}"):
                        row = {
                            "title": r.get("title"),
                            "authors": r.get("authors"),
                            "publisher": r.get("publisher"),
                            "publishedDate": r.get("publishedDate"),
                            "pageCount": r.get("pageCount"),
                            "categories": r.get("categories"),
                            "isbn_10": r.get("isbn_10"),
                            "isbn_13": r.get("isbn_13"),
                            "language": r.get("language"),
                            "infoLink": r.get("infoLink"),
                            "thumbnail": r.get("thumbnail"),
                            "date_read": date_read.strftime("%Y-%m-%d"),
                            "notes": notes,
                            "source": r.get("source"),
                        }
                        st.session_state.library = pd.concat([
                            st.session_state.library,
                            pd.DataFrame([row])
                        ], ignore_index=True)
                        st.success("추가되었습니다! 아래 '내 기록'에서 확인하세요.")
    else:
        st.warning("검색 결과가 없어요. 검색어/ISBN을 확인해 주세요.")

st.markdown("---")

# -----------------------------
# 내 기록 (데이터 편집)
# -----------------------------
st.subheader("📖 내 기록 (편집 가능)")

if st.session_state.library.empty:
    st.info("아직 추가된 책이 없어요. 위에서 검색해 추가해 보세요!")
else:
    # 보기/편집 테이블
    edited = st.data_editor(
        st.session_state.library,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "title": st.column_config.TextColumn("제목", required=True),
            "authors": st.column_config.TextColumn("저자"),
            "publisher": st.column_config.TextColumn("출판사"),
            "publishedDate": st.column_config.TextColumn("출간"),
            "pageCount": st.column_config.NumberColumn("쪽수", step=1),
            "categories": st.column_config.TextColumn("장르/카테고리"),
            "isbn_10": st.column_config.TextColumn("ISBN-10"),
            "isbn_13": st.column_config.TextColumn("ISBN-13"),
            "language": st.column_config.TextColumn("언어"),
            "infoLink": st.column_config.LinkColumn("정보 링크"),
            "thumbnail": st.column_config.TextColumn("표지 URL"),
            "date_read": st.column_config.TextColumn("읽은 날짜 (YYYY-MM-DD)"),
            "notes": st.column_config.TextColumn("메모"),
            "source": st.column_config.TextColumn("출처"),
        },
        hide_index=True,
    )
    st.session_state.library = edited

    # 간단 통계
    stats1, stats2, stats3, stats4 = st.columns(4)
    with stats1:
        st.metric("총 권수", len(edited))
    with stats2:
        st.metric("고유 저자 수", edited["authors"].fillna("").apply(lambda s: [a.strip() for a in s.split(",") if a.strip()] ).explode().nunique())
    with stats3:
        pages = pd.to_numeric(edited["pageCount"], errors="coerce").dropna()
        st.metric("총 페이지", int(pages.sum()) if len(pages) else 0)
    with stats4:
        this_year = str(datetime.today().year)
        st.metric("올해 읽은 책", int((edited["date_read"].fillna("").str.startswith(this_year)).sum()))

st.markdown("---")

# -----------------------------
# 분석 대시보드
# -----------------------------
st.subheader("📈 분석 대시보드")

if st.session_state.library.empty:
    st.info("데이터가 있어야 분석할 수 있어요. 위에서 책을 추가해 주세요.")
else:
    df = st.session_state.library.copy()
    # 날짜 파싱
    df["date_read_parsed"] = pd.to_datetime(df["date_read"], errors="coerce")

    # 1) 독서량 추이 그래프 (월별)
    st.markdown("#### 📊 월별 독서량 추이")
    # 최근 12개월 보기 토글
    only_12 = st.toggle("최근 12개월만 보기", value=True)
    ts = (
        df.dropna(subset=["date_read_parsed"]) 
          .assign(month=lambda x: x["date_read_parsed"].dt.to_period("M").dt.to_timestamp())
          .groupby("month").size().rename("count").reset_index()
          .sort_values("month")
    )
    if only_12 and not ts.empty:
        cutoff = datetime.today() - relativedelta(months=11)
        ts = ts[ts["month"] >= cutoff.replace(day=1)]

    if ts.empty:
        st.write(":grey[표시할 데이터가 없어요.]")
    else:
        fig1, ax1 = plt.subplots()
        ax1.plot(ts["month"], ts["count"], marker="o")
        ax1.set_xlabel("월")
        ax1.set_ylabel("권수")
        ax1.set_title("월별 읽은 권수")
        ax1.grid(True, linestyle=":", alpha=0.4)
        st.pyplot(fig1, use_container_width=True)

    st.markdown("---")

    # 2) 가장 많이 읽은 장르 워드클라우드
    st.markdown("#### ☁️ 장르/카테고리 워드클라우드")
    cats = df["categories"].dropna().astype(str)
    tokens: List[str] = []
    for c in cats:
        # 카테고리 문자열을 쉼표/슬래시로 구분
        parts = [p.strip() for p in c.replace("/", ",").split(",") if p.strip()]
        tokens.extend(parts)
    if not tokens:
        st.write(":grey[장르 정보가 없어 워드클라우드를 만들 수 없어요.]")
    else:
        freq = pd.Series(tokens).value_counts().to_dict()
        wc = WordCloud(width=1000, height=500, background_color="white")
        wc.generate_from_frequencies(freq)
        fig2, ax2 = plt.subplots(figsize=(10,5))
        ax2.imshow(wc, interpolation="bilinear")
        ax2.axis("off")
        st.pyplot(fig2, use_container_width=True)

    st.markdown("---")

    # 3) 출판사/저자 TOP N
    st.markdown("#### 🏷️ 가장 많이 읽은 저자/출판사")
    top_n = st.slider("TOP N", 3, 15, 5, key="topn")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**저자 TOP**")
        authors_series = df["authors"].fillna("").apply(lambda s: [a.strip() for a in s.split(",") if a.strip()])
        top_authors = pd.Series([a for lst in authors_series for a in lst]).value_counts().head(top_n)
        if top_authors.empty:
            st.write(":grey[데이터 없음]")
        else:
            fig3, ax3 = plt.subplots()
            top_authors.sort_values().plot(kind="barh", ax=ax3)
            ax3.set_xlabel("권수")
            st.pyplot(fig3, use_container_width=True)

    with c2:
        st.markdown("**출판사 TOP**")
        top_pubs = df["publisher"].dropna().astype(str).value_counts().head(top_n)
        if top_pubs.empty:
            st.write(":grey[데이터 없음]")
        else:
            fig4, ax4 = plt.subplots()
            top_pubs.sort_values().plot(kind="barh", ax=ax4)
            ax4.set_xlabel("권수")
            st.pyplot(fig4, use_container_width=True)

# -----------------------------
# 푸터
# -----------------------------
st.markdown("---")
st.caption("© 독서 기록 & 분석 — Streamlit 예제. Open Library 및 Google Books 메타데이터를 사용합니다.")

