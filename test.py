st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://plus.unsplash.com/premium_photo-1698084059448-5bdc536e083a?q=80&w=715&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"); /* 도서관 이미지 URL */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        position: relative;
    }

    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.4); /* 검은색 40% 투명 */
        z-index: 0;
    }

    /* 내용물이 배경 위로 올라오도록 */
    .stApp > div {
        position: relative;
        z-index: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="📚 나만의 독서 일기장", layout="wide")

# --- 초기 세션 상태 ---
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(
        columns=["title", "authors", "publisher", "publishedDate", "categories"]
    )

# --- 책 기록 입력 ---
st.header("📖 나만의 독서 일기장")
with st.form("book_form", clear_on_submit=True):  # ✅ 제출 후 자동 초기화
    title = st.text_input("책 제목")
    authors = st.text_input("저자 (여러 명은 ,로 구분)")
    publisher = st.text_input("출판사")
    published_date = st.date_input("출간일", value=datetime.date.today())  # ✅ 오늘 날짜 기본값
    categories = st.text_input("장르 (여러 개면 ,로 구분)")

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

# --- 저장된 책 목록 ---
st.header("📚 저장된 책 목록")
if not st.session_state["books"].empty:
    st.dataframe(st.session_state["books"], use_container_width=True)

    # 📥 CSV 다운로드
    csv = st.session_state["books"].to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV 다운로드", csv, "books.csv", "text/csv")

    # 📤 CSV 업로드
    uploaded_file = st.file_uploader("📤 CSV 불러오기", type=["csv"])
    if uploaded_file is not None:
        st.session_state["books"] = pd.read_csv(uploaded_file)
        st.success("✅ CSV 불러오기 완료!")

    # 🗑️ 책 삭제 기능
    st.subheader("🗑️ 책 삭제하기")
    book_list = st.session_state["books"]["title"].tolist()
    book_to_delete = st.selectbox("삭제할 책 선택", [""] + book_list)
    if st.button("삭제"):
        if book_to_delete:
            st.session_state["books"] = st.session_state["books"][
                st.session_state["books"]["title"] != book_to_delete
            ]
            st.success(f"✅ '{book_to_delete}' 삭제됨!")
        else:
            st.warning("⚠️ 삭제할 책을 선택하세요.")

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
    ax.set_xlabel("Publication year")   # ✅ 가로축
    ax.set_ylabel("Number of books read")  # ✅ 세로축
    st.pyplot(fig)

    # 2. 저자 TOP 10
    st.subheader("👩‍💻 저자 TOP 10")
    authors_series = edited["authors"].fillna("").apply(
        lambda s: [a.strip() for a in s.split(",") if a.strip()]
    ).explode()
    top_authors = authors_series.value_counts().head(10)
    st.bar_chart(top_authors)
