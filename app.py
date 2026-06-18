import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ===== 페이지 설정 =====
st.set_page_config(page_title="한강 수질 분석", layout="wide")
st.title("🌊 한강 수질 오염 분석 대시보드")
st.markdown("**분석 기간:** 2023년 7월 ~ 2026년 6월 | **측정 지점:** 5개 | **지표:** 5개")

# ===== 데이터 로드 =====
@st.cache_data
def load_data():
    df = pd.read_csv('./data/processed/hangang_final.csv')
    df['년/월/일'] = pd.to_datetime(df['년/월/일'])
    df['년월'] = df['년/월/일'].dt.to_period('M')
    df['년도'] = df['년/월/일'].dt.year
    
    # 계절 구분
    def get_season(month):
        if month in [3, 4, 5]:
            return '봄'
        elif month in [6, 7, 8]:
            return '여름'
        elif month in [9, 10, 11]:
            return '가을'
        else:
            return '겨울'
    
    df['계절'] = df['년/월/일'].dt.month.apply(get_season)
    return df

df = load_data()

# ===== 월별 평균값 =====
@st.cache_data
def get_monthly():
    monthly = df.groupby(['년월', '측정소명'])[['DO(㎎/L)', 'BOD(㎎/L)', 'COD(㎎/L)', 'TP(㎎/L)', 'TN(㎎/L)']].mean().reset_index()
    monthly['년월'] = monthly['년월'].dt.to_timestamp()
    return monthly

monthly = get_monthly()

# ===== 계절별 평균값 =====
@st.cache_data
def get_seasonal():
    seasonal_avg = df.groupby(['계절', '측정소명'])[['DO(㎎/L)', 'BOD(㎎/L)', 'COD(㎎/L)', 'TP(㎎/L)', 'TN(㎎/L)']].mean().reset_index()
    season_order = {'봄': 1, '여름': 2, '가을': 3, '겨울': 4}
    seasonal_avg['season_num'] = seasonal_avg['계절'].map(season_order)
    seasonal_avg = seasonal_avg.sort_values('season_num')
    return seasonal_avg

seasonal_avg = get_seasonal()

# ===== 년도별 평균값 =====
@st.cache_data
def get_yearly():
    yearly = df.groupby(['년도', '측정소명'])[['DO(㎎/L)', 'BOD(㎎/L)', 'COD(㎎/L)', 'TP(㎎/L)', 'TN(㎎/L)']].mean().reset_index()
    yearly['년도'] = yearly['년도'].astype(str)
    return yearly

yearly = get_yearly()

# ===== 지점별 평균값 =====
@st.cache_data
def get_point_avg():
    point_order = ['팔당댐2', '성내천', '보광', '노량진', '영등포']
    point_avg = df.groupby('측정소명')[['DO(㎎/L)', 'BOD(㎎/L)', 'COD(㎎/L)', 'TP(㎎/L)', 'TN(㎎/L)']].mean().reset_index()
    point_avg['측정소명'] = pd.Categorical(point_avg['측정소명'], categories=point_order, ordered=True)
    point_avg = point_avg.sort_values('측정소명')
    return point_avg, point_order

point_avg, point_order = get_point_avg()

# ===== 탭 설정 =====
tab1, tab2, tab3, tab4 = st.tabs(["📊 박스플롯 분석 (##2)", "📈 평균값 비교 (##3)", "⏱️ 시계열 분석 (##4)", "📋 최종 결론"])

# ===== Tab 1: 박스플롯 분석 =====
with tab1:
    st.header("##2 박스플롯 분석")
    st.markdown("지점별 오염도 분포를 비교합니다.")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        indicator = st.selectbox("지표 선택", ["DO(㎎/L)", "BOD(㎎/L)", "COD(㎎/L)", "TP(㎎/L)", "TN(㎎/L)"], key="tab1")
    
    with col1:
        fig = px.box(df, x="측정소명", y=indicator, 
                     title=f"지점별 {indicator} 분포",
                     category_orders={"측정소명": point_order})
        st.plotly_chart(fig, use_container_width=True)

# ===== Tab 2: 평균값 비교 =====
with tab2:
    st.header("##3 지점별 평균값 비교")
    st.markdown("상류→하류 오염도 변화를 비교합니다.")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        indicator = st.selectbox("지표 선택", ["DO(㎎/L)", "BOD(㎎/L)", "COD(㎎/L)", "TP(㎎/L)", "TN(㎎/L)"], key="tab2")
    
    with col1:
        fig = px.bar(point_avg, x="측정소명", y=indicator, 
                     title=f"지점별 {indicator} 평균값",
                     category_orders={"측정소명": point_order})
        fig.update_traces(marker_color='#7FDBCA') 
        st.plotly_chart(fig, use_container_width=True)

# ===== Tab 3: 시계열 분석 =====
with tab3:
    st.header("##4 시계열 분석")
    st.markdown("월별, 계절별, 년도별 오염도 변화 추세를 분석합니다.")
    
    # 1. 지점별 평균값
    st.subheader("📊 지점별 평균값 (상류→하류)")
    display_point_avg = point_avg.round(2)  # 소수점 2자리로 반올림
    st.dataframe(display_point_avg, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # 2. 월별 시계열
    st.subheader("📈 월별 변화 추이 (36개월)")
    col1, col2 = st.columns([3, 1])
    with col2:
        indicator_monthly = st.selectbox("지표 선택", ["DO(㎎/L)", "BOD(㎎/L)", "COD(㎎/L)", "TP(㎎/L)", "TN(㎎/L)"], key="monthly")
    with col1:
        fig_monthly = px.line(monthly, x='년월', y=indicator_monthly, color='측정소명',
                              title=f'지점별 {indicator_monthly} 월별 변화 추이', markers=True)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    st.divider()
    
    # 3. 계절별 시계열
    st.subheader("🌍 계절별 변화 (4계절)")
    col1, col2 = st.columns([3, 1])
    with col2:
        indicator_seasonal = st.selectbox("지표 선택", ["DO(㎎/L)", "BOD(㎎/L)", "COD(㎎/L)", "TP(㎎/L)", "TN(㎎/L)"], key="seasonal")
    with col1:
        fig_seasonal = px.line(seasonal_avg, x='계절', y=indicator_seasonal, color='측정소명',
                               title=f'지점별 {indicator_seasonal} 계절별 변화', markers=True,
                               category_orders={'계절': ['봄', '여름', '가을', '겨울']})
        st.plotly_chart(fig_seasonal, use_container_width=True)
    
    st.divider()
    
    # 4. 년도별 시계열
    st.subheader("📅 년도별 변화 (장기 추세)")
    col1, col2 = st.columns([3, 1])
    with col2:
        indicator_yearly = st.selectbox("지표 선택", ["DO(㎎/L)", "BOD(㎎/L)", "COD(㎎/L)", "TP(㎎/L)", "TN(㎎/L)"], key="yearly")
    with col1:
        year_order = sorted(yearly['년도'].unique())
        fig_yearly = px.line(yearly, x='년도', y=indicator_yearly, color='측정소명',
                             title=f'지점별 {indicator_yearly} 년도별 변화', markers=True,
                             category_orders={'년도': year_order})
        fig_yearly.update_xaxes(type='category')
        st.plotly_chart(fig_yearly, use_container_width=True)
