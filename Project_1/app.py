import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
# LOAD DATA (directly from folder)
# -------------------------------
time_csv = "google_trends_interest.csv"
region_csv = "google_trends_region.csv"
related_csv = "google_trends_ai_related.csv"

if os.path.exists(time_csv):
    df = pd.read_csv(time_csv, parse_dates=['date'], index_col='date')

    # Drop 'isPartial' if exists
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
        fig = px.line(df, x=df.index, y=keywords,
                      labels={"value": "Search Interest", "date": "Date"},
                      title="Search Interest Over Time")
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # YEARLY AVERAGE
    # -------------------------------
    st.subheader("📊 Average Yearly Interest")
    yearly = df.resample("Y").mean()
    fig2 = px.line(yearly, x=yearly.index, y=yearly.columns, markers=True,
                   labels={"value": "Avg Search Interest", "date": "Year"},
                   title="Average Yearly Search Interest")
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # CORRELATION HEATMAP
    # -------------------------------
    st.subheader("🔗 Correlation Between Keywords")
    corr = df.corr()
    fig3 = px.imshow(corr, text_auto=True, color_continuous_scale="Blues", title="Correlation Heatmap")
    st.plotly_chart(fig3, use_container_width=True)

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

    # -------------------------------
    # REGIONAL INTEREST
    # -------------------------------
    if os.path.exists(region_csv):
        st.subheader("🌍 Regional Interest")
        region_df = pd.read_csv(region_csv, index_col=0)
        top_regions = region_df[selected_keyword].sort_values(ascending=False).head(10)
        fig6 = px.bar(top_regions, x=top_regions.values, y=top_regions.index, orientation="h",
                      labels={"x": "Search Interest", "index": "Region"},
                      title=f"Top 10 Regions Interested in {selected_keyword}")
        st.plotly_chart(fig6, use_container_width=True)

    # -------------------------------
    # RELATED QUERIES
    # -------------------------------
    if os.path.exists(related_csv):
        st.subheader("🔍 Related Queries")
        related_df = pd.read_csv(related_csv, index_col=0)
        fig7 = px.bar(related_df.head(10), x="value", y="query", orientation="h",
                      labels={"value": "Popularity", "query": "Related Query"},
                      title=f"Top Related Queries for {selected_keyword}")
        st.plotly_chart(fig7, use_container_width=True)

    # -------------------------------
    # EXTRA PLOTS (added for richness)
    # -------------------------------

    # Seasonal trends (Monthly Average)
    st.subheader("📅 Seasonal Patterns (Monthly Average)")
    monthly = df.resample("M").mean()
    fig8 = px.line(monthly, x=monthly.index, y=selected_keyword,
                   title=f"Monthly Average Interest for {selected_keyword}")
    st.plotly_chart(fig8, use_container_width=True)

    # Rolling correlation between two keywords
    st.subheader("🔄 Rolling Correlation Between Two Keywords")
    k1, k2 = st.selectbox("Keyword 1", df.columns, index=0), st.selectbox("Keyword 2", df.columns, index=1)
    rolling_corr = df[k1].rolling(window=12).corr(df[k2])
    fig9 = px.line(x=df.index, y=rolling_corr,
                   labels={"x": "Date", "y": "Correlation"},
                   title=f"12-Month Rolling Correlation: {k1} vs {k2}")
    st.plotly_chart(fig9, use_container_width=True)

    # Distribution of interest values
    st.subheader("📦 Distribution of Search Interest")
    fig10 = px.histogram(df, x=selected_keyword, nbins=20,
                         title=f"Distribution of Search Interest for {selected_keyword}")
    st.plotly_chart(fig10, use_container_width=True)

else:
    st.error("❌ 'interest_over_time.csv' not found in this folder. Please add the file.")
