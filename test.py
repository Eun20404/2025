import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📚 나만의 도서관 일기장 ")

# 세션 상태에 데이터 저장
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
    st.session_state["published_date"] = None

# 입력창 (Form)
with st.form("book_form"):
    title = st.text_input("책 제목", key="title")
    authors = st.text_input("저자 (여러 명은 ,로 구분)", key="authors")
    publisher = st.text_input("출판사", key="publisher")
    published_date = st.date_input("출간일", key="published_date")
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
        reset_inputs()  # 입력값 초기화

# 기록이 있을 때만 분석 & 출력
if not st.session_state["books"].empty:
    st.subheader("📖 나의 독서 기록")
    st.dataframe(st.session_state["books"])

    # CSV 다운로드
    csv = st.session_state["books"].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="💾 CSV로 저장하기",
        data=csv,
        file_name="reading_log.csv",
        mime="text/csv",
    )

    # 간단 분석
    st.subheader("📊 독서 분석")
    c1, c2 = st.columns(2)

    with c1:
        st.metric("총 독서량", len(st.session_state["books"]))

    with c2:
        st.metric(
            "고유 저자 수",
            st.session_state["books"]["authors"]
            .fillna("")
            .str.split(",")
            .explode()
            .str.strip()
            .nunique()
        )

    # 출간연도별 독서량
    st.subheader("출간 연도별 독서량")
    df = st.session_state["books"].copy()
    df["publishedDate"] = pd.to_datetime(df["publishedDate"], errors="coerce")
    yearly = df.dropna(subset=["publishedDate"]).groupby(df["publishedDate"].dt.year).size()
    st.line_chart(yearly)

else:
    st.info("📥 아직 기록이 없어요. 위에 입력창에서 책을 추가해보세요!")
