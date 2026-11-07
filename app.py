import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ===== 페이지 설정 =====
st.set_page_config(page_title="한강 수질 분석", layout="wide")
st.title("🌊 한강 수질 오염 분석 대시보드")
st.markdown("**분석 기간:** 2023년 7월 ~ 2026년 4월 (34개월) | **측정 지점:** 5개 | **지표:** 5개")

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
        fig.update_traces(marker_color='#FF6B35')  # 성내천 색상(주황색)
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
    st.subheader("📈 월별 변화 추이 (34개월)")
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

# ===== Tab 4: 최종 결론 =====
with tab4:
    st.header("📋 최종 결론")
    st.markdown("34개월 분석 데이터를 통해 관찰된 사실과 해석")
    
    # 1. 관찰된 사실
    st.subheader("🔍 관찰된 사실")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. 지점별 수질 차이**
        
        상류 → 하류:
        - DO: 11.3 (팔당댐2) → 9.3 (성내천) → 10.1 (영등포)
        - TP: 0.034 (팔당댐2) → 0.085 (성내천) → 0.045 (영등포)
        - TN: 2.48 (팔당댐2) → 4.26 (노량진) → 3.50 (영등포)

        성내천은 DO가 가장 낮고 TP가 가장 높음
        """)
        
        st.markdown("""
        **3. 년도별 변화**
        
        - 2023년 (7~12월): DO 9.5
        - 2024년: DO 10.5
        - 2025년: DO 9.7
        - 2026년 (1~4월): DO 12.1

        측정 기간이 달라 연도별 추세로 보기 어려움
        """)
    
    with col2:
        st.markdown("""
        **2. 계절별 변화**
        
        여름 vs 겨울:
        - DO: 여름 7.8 vs 겨울 13.0 (약 1.7배)

        여름에 DO가 가장 낮고, 겨울에 가장 높음
        """)
        
        st.markdown("""
        **4. 환경기준 평가**
        
        전체적으로 환경기준 충족
        - DO: 10.3 (Ia: ≥7.5) ✅
        - BOD: 1.8 (II: ≤3) ✅
        - TP: 0.060 (II: ≤0.1) ✅
        - 성내천 TP: 0.085 ⚠️ (기준 0.1에 근접)
        """)
    
    st.divider()
    
    # 2. 환경기준 평가
    st.subheader("📋 환경기준 평가")
    
    st.markdown("""
    | 지표 | 기준 | 한강 평균 | 평가 |
    |:---:|:---:|:---:|:---:|
    | **DO** | Ia≥7.5 | 10.3 | ✅ 합격 |
    | **BOD** | II≤3 | 1.8 | ✅ 합격 |
    | **COD** | II≤5 | 4.1 | ✅ 합격 |
    | **TP** | II≤0.1 | 0.060 | ✅ 합격 |
    | | | (성내천 0.085) | ⚠️ 주의 |
    
    **평가:** 대부분의 지점과 지표가 환경기준을 만족합니다.
    (성내천의 TP만 환경기준에 가깝습니다)
    """)
    
    st.divider()
    
    # 3. 해석
    st.subheader("💡 해석")
    
    st.markdown("""
    **성내천의 오염도가 높다**
    
    성내천은 DO가 가장 낮고 TP가 가장 높다. BOD와 COD는 보광이 가장 높다.
    상류의 양호한 수질이 성내천을 거치면서 악화되고, 
    하류에서 조금 회복되지만 여전히 상류보다는 낮다.
    
    **영양염(TN)은 중·하류에서 높게 나타난다**

    상류 팔당댐2 2.48 mg/L에서 노량진 4.26 mg/L로 약 1.7배 높아지고, 영등포는 3.50 mg/L이다.
    
    **계절별 수질 변동은 명확하다**
    
    여름에 DO가 가장 낮고(7.8 mg/L), 겨울에 가장 높다(13.0 mg/L).
    높은 수온에서는 물에 녹는 산소가 줄어드는 것으로 추정된다.
    이는 자연적인 수질 변동 패턴이다.
    
    **2026년 DO 평균은 추세로 판단하기 어렵다**

    2026년 1~4월 DO 평균(12.1 mg/L)은 다른 해보다 높지만, 4개월치 값이라 추세라고 단정할 수 없다.
    """)
    
    st.divider()
    
    # 4. 결론
    st.subheader("📋 결론")
    
    st.success("""
    **한강의 수질은 전체적으로 환경기준을 만족한다.**
    
    대부분의 지점과 지표가 환경기준 범위 내에 있다.
    """)
    
    st.warning("""
    **성내천의 오염도가 특히 높다.**
    
    - DO가 가장 낮음 (9.3 ㎎/L)
    - TP가 가장 높음 (0.085 ㎎/L, 기준 0.1에 근접)
    - BOD·COD는 보광이 가장 높음
    """)
    
    st.info("""
    **성내천의 영향이 한강 전체에 미친다.**
    
    상류는 양호하나, 성내천 유입 후 수질이 악화된다.
    하류에서 일부 회복되지만, 여전히 상류보다 낮은 수준이다.
    """)
    
    st.markdown("""
    **영양염 농도는 상류보다 중·하류에서 높다.**

    TN: 2.48 (팔당댐2) → 4.26 (노량진, 약 1.7배) → 3.50 (영등포)

    중·하류 구간에서 질소가 더해지는 것으로 보이지만, 원인은 이 데이터로 확인할 수 없다.
    """)
    
    st.markdown("""
    **계절별 수질 변동은 자연적 패턴을 따른다.**
    
    여름에 DO가 가장 낮은 것은 높은 수온과 관련된 것으로 해석된다.
    이는 통제하기 어려운 자연적 변동이다.
    """)
    
    st.markdown("""
    **2026년 DO 평균만으로는 개선 여부를 판단할 수 없다.**

    2026년 1~4월 DO 평균이 12.1 mg/L로 높게 나타났지만, 표본이 적어 개선으로 단정할 수 없다.
    """)
    
    st.divider()
    
    # 5. 주의사항
    st.subheader("⚠️ 주의사항")
    
    st.warning("""
    **이 분석의 한계**
    
    - 34개월(2023년 7월 ~ 2026년 4월) 데이터만을 기반으로 함
    - 성내천 오염의 원인은 파악하지 못함
    - 계절 변화 외 다른 요인이 있을 수 있음
    - 강수량, 기온 등 여러 요소의 영향을 받음
    """)
    
    st.info("""
    **분석 정보**
    
    분석 기간: 2023년 7월 ~ 2026년 4월 (34개월)  
    측정 지점: 5개 (팔당댐2, 성내천, 보광, 노량진, 영등포)  
    주요 지표: DO, BOD, COD, TP, TN (5개)
    """)

# ===== Footer =====
st.divider()
st.markdown("""
---
**한강 수질 오염 분석 대시보드**
""")
