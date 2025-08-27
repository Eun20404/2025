import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="📚 독서 기록 & 분석 앱", layout="wide")

# 초기 세션 상태 설정
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(
        columns=["title", "authors", "publisher", "publishedDate", "categories"]
    )

# 입력값 초기화 함수
def reset_inputs():
    st.session_state["title"] = ""
    st.session_state["authors"] = ""
    st.session_state["publisher"] = ""
    st.session_state["categories"] = ""
    st.session_state["published_date"] = datetime.date.today()  # ✅ 오늘 날짜로 초기화

# --- 입력 폼 ---
st.header("📖 책 기록하기")
with st.form("book_form"):
    title = st.text_input("책 제목", key="title")
    authors = st.text_input("저자 (여러 명은 ,로 구분)", key="authors")
    publisher = st.text_input("출판사", key="publisher")
    published_date = st.date_input("출간일", key="published_date", value=datetime.date.today())
    categories = st.text_input("장르 (여러 개면 ,로 구분)", key="categories")

    submitted = st.form_submit_button("추가하기")
    if submitted:
        new_row = {
            "title": title,
            "authors": authors,
            "publisher": publisher,
            "publishedDate": str(published_date),
            "categories": categories,
        }
        st.session_state["books"] = pd.concat(
            [st.session_state["books"], pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success(f"✅ '{title}' 저장됨!")
        reset_inputs()  # 입력칸 초기화

# --- 저장된 책 목록 ---
st.header("📚 저장된 책 목록")
if not st.session_state["books"].empty:
    for i, row in st.session_state["books"].iterrows():
        with st.container():
            cols = st.columns([6, 1])
            cols[0].write(f"**{row['title']}** | 저자: {row['authors']} | 출판사: {row['publisher']} | 출간일: {row['publishedDate']} | 장르: {row['categories']}")
            if cols[1].button("❌ 삭제", key=f"delete_{i}"):
                st.session_state["books"].drop(i, inplace=True)
                st.session_state["books"].reset_index(drop=True, inplace=True)
                st.experimental_rerun()

    # CSV 다운로드
    csv = st.session_state["books"].to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV 다운로드", csv, "books.csv", "text/csv")

    # CSV 업로드
    uploaded_file = st.file_uploader("📤 CSV 불러오기", type=["csv"])
    if uploaded_file is not None:
        st.session_state["books"] = pd.read_csv(uploaded_file)
        st.success("✅ CSV 불러오기 완료!")

else:
    st.info("아직 저장된 책이 없습니다. 위 입력창에서 책을 추가해 보세요!")

# --- 분석 ---
if not st.session_state["books"].empty:
    st.header("📊 독서 데이터 분석")
    edited = st.session_state["books"].copy()

    # 출간연도 추출
    edited["year"] = pd.to_datetime(edited["publishedDate"], errors="coerce").dt.year

    # 1. 연도별 독서량 추이
    st.subheader("📈 연도별 독서량 추이")
    year_count = edited["year"].value_counts().sort_index()
    fig, ax = plt.subplots()
    year_count.plot(kind="bar", ax=ax)
    ax.set_xlabel("Publication year")        # ✅ 가로축
    ax.set_ylabel("Number of books read")    # ✅ 세로축
    st.pyplot(fig)

    # 2. 저자 TOP 10
    st.subheader("👩‍💻 저자 TOP 10")
    authors_series = edited["authors"].fillna("").apply(
        lambda s: [a.strip() for a in s.split(",") if a.strip()]
    ).explode()
    top_authors = authors_series.value_counts().head(10)
    st.bar_chart(top_authors)
    
