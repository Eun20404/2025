import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="📚 독서 기록 & 분석 앱", layout="wide")

# --- 초기 세션 상태 ---
if "books" not in st.session_state:
    st.session_state["books"] = pd.DataFrame(
        columns=["title", "authors", "publisher", "publishedDate", "categories"]
    )
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

# --- 책 기록 입력 ---
st.header("📖 책 기록하기")
with st.form("book_form", clear_on_submit=True):  # ✅ clear_on_submit 사용
    title = st.text_input("책 제목")
    authors = st.text_input("저자 (여러 명은 ,로 구분)")
    publisher = st.text_input("출판사")
    published_date = st.date_input("출간일", value=datetime.date.today())
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
