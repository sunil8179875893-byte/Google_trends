import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Google Trends Analytics", layout="wide")
st.title("📊 Google Trends Data Analytics Dashboard")
st.markdown(
    """
    This dashboard analyzes **Google Search Trends** data for selected topics.  
    It shows **time series trends, correlations, regional insights, and related queries**  
    — providing meaningful insights for business and technology.
    """
)

# -------------------------------
# FILE UPLOAD
# -------------------------------
st.sidebar.header("⚙️ Controls")
uploaded_file = st.sidebar.file_uploader("Upload Google Trends CSV (interest_over_time)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=['date'], index_col='date')

    # Drop 'isPartial' column if present
    if 'isPartial' in df.columns:
        df = df.drop(columns=['isPartial'])

    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head())

    # -------------------------------
    # TIME SERIES PLOT
    # -------------------------------
    st.subheader("📈 Search Trends Over Time")
    keywords = st.multiselect("Select Keywords to Plot", df.columns.tolist(), default=df.columns.tolist())
    
    if keywords:
        fig = px.line(df, x=df.index, y=keywords, labels={"value": "Search Interest", "date": "Date"}, title="Search Interest Over Time")
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            f"✅ The chart shows how selected keywords evolved between **{df.index.min().date()}** and **{df.index.max().date()}**. "
            "Notice the **spikes** and **growth trends** that often correspond to global events or announcements."
        )

    # -------------------------------
    # YEARLY AVERAGE
    # -------------------------------
    st.subheader("📊 Average Yearly Interest")
    yearly = df.resample("Y").mean()
    fig2 = px.line(yearly, x=yearly.index, y=yearly.columns, markers=True,
                   labels={"value": "Avg Search Interest", "date": "Year"},
                   title="Average Yearly Search Interest")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("✅ This chart shows the **long-term growth trend** of each topic, smoothed by yearly averages.")

    # -------------------------------
    # CORRELATION HEATMAP
    # -------------------------------
    st.subheader("🔗 Correlation Between Keywords")
    corr = df.corr()
    fig3 = px.imshow(corr, text_auto=True, color_continuous_scale="Blues", title="Correlation Heatmap")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("✅ High correlation (close to 1) means that topics trend together (e.g., *AI* and *Data Analytics*).")

    # -------------------------------
    # PEAK ANALYSIS
    # -------------------------------
    st.subheader("📌 Top 5 Peaks in Interest")
    selected_keyword = st.selectbox("Choose a Keyword", df.columns.tolist())
    peaks = df[selected_keyword].sort_values(ascending=False).head(5)
    fig4 = px.line(df, x=df.index, y=selected_keyword, title=f"Peaks in {selected_keyword} Search Trend")
    fig4.add_scatter(x=peaks.index, y=peaks.values, mode="markers+text",
                     marker=dict(size=12, color="red"),
                     text=[f"Peak: {v}" for v in peaks.values],
                     textposition="top center", name="Peaks")
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(f"✅ The red points highlight the **highest interest periods** for *{selected_keyword}*.")

    # -------------------------------
    # MOVING AVERAGE
    # -------------------------------
    st.subheader("📉 Trend Smoothing (Moving Average)")
    window = st.slider("Select Rolling Window (Months)", min_value=3, max_value=24, value=12)
    df_ma = df[selected_keyword].rolling(window=window).mean()
    fig5 = px.line(x=df.index, y=[df[selected_keyword], df_ma],
                   labels={"x": "Date", "y": "Search Interest"},
                   title=f"{selected_keyword} Trend with {window}-Month Moving Average")
    fig5.update_traces(mode="lines")
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("✅ The moving average helps **smooth short-term fluctuations** to reveal long-term patterns.")

    # -------------------------------
    # REGIONAL INTEREST
    # -------------------------------
    st.subheader("🌍 Regional Interest (Upload Region CSV)")
    region_file = st.file_uploader("Upload Regional CSV (interest_by_region)", type="csv")
    if region_file:
        region_df = pd.read_csv(region_file, index_col=0)
        top_regions = region_df[selected_keyword].sort_values(ascending=False).head(10)
        fig6 = px.bar(top_regions, x=top_regions.values, y=top_regions.index, orientation="h",
                      labels={"x": "Search Interest", "index": "Region"},
                      title=f"Top 10 Regions Interested in {selected_keyword}")
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown("✅ This chart highlights **where the interest is strongest geographically**.")

    # -------------------------------
    # RELATED QUERIES
    # -------------------------------
    st.subheader("🔍 Related Queries (Upload Related CSV)")
    related_file = st.file_uploader("Upload Related Queries CSV", type="csv")
    if related_file:
        related_df = pd.read_csv(related_file, index_col=0)
        fig7 = px.bar(related_df.head(10), x="value", y="query", orientation="h",
                      labels={"value": "Popularity", "query": "Related Query"},
                      title=f"Top Related Queries for {selected_keyword}")
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown("✅ These queries provide context on **what people search alongside the main keyword**.")

else:
    st.info("👈 Upload your Google Trends CSV to get started.")
