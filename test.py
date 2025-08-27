st.header("📊 독서 데이터 분석")

if not edited.empty:
    # 요약 통계
    st.subheader("요약 통계")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("총 독서량", len(edited))

    with c2:
        st.metric(
            "고유 저자 수",
            edited["authors"]
            .fillna("")
            .apply(lambda s: [a.strip() for a in s.split(",") if a.strip()])
            .explode()
            .nunique()
        )

    with c3:
        st.metric(
            "고유 출판사 수",
            edited["publisher"]
            .fillna("")
            .apply(lambda s: [p.strip() for p in s.split(",") if p.strip()])
            .explode()
            .nunique()
        )

    # 출간 연도별 독서량 추이
    st.subheader("📈 출간 연도별 독서량 추이")
    if "publishedDate" in edited.columns:
        edited["publishedDate"] = pd.to_datetime(edited["publishedDate"], errors="coerce")
        yearly = edited.dropna(subset=["publishedDate"]).groupby(
            edited["publishedDate"].dt.to_period("Y")
        ).size()
        st.line_chart(yearly)

    # 장르 워드클라우드
    st.subheader("☁️ 가장 많이 읽은 장르")
    if "categories" in edited.columns:
        all_categories = (
            edited["categories"]
            .dropna()
            .str.split(",")
            .explode()
            .str.strip()
        )
        if not all_categories.empty:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt

            wc = WordCloud(width=800, height=400, background_color="white").generate(
                " ".join(all_categories)
            )
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

    # 저자 / 출판사 TOP 10
    st.subheader("📚 저자 / 출판사 TOP 10")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**저자 TOP 10**")
        if "authors" in edited.columns:
            top_authors = (
                edited["authors"]
                .dropna()
                .str.split(",")
                .explode()
                .str.strip()
                .value_counts()
                .head(10)
            )
            st.bar_chart(top_authors)

    with c2:
        st.markdown("**출판사 TOP 10**")
        if "publisher" in edited.columns:
            top_publishers = (
                edited["publisher"]
                .dropna()
                .str.split(",")
                .explode()
                .str.strip()
                .value_counts()
                .head(10)
            )
            st.bar_chart(top_publishers)
