import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data import records

st.set_page_config(
    page_title="AI 진료기록 요약 검토 시스템",
    layout="wide"
)

st.title("AI 진료기록 요약 검토 시스템")
st.write("가상의 SOAP 형식 진료기록을 바탕으로 일반 요약과 구조화 요약의 핵심정보 보존 여부를 비교합니다.")

st.divider()

# 세션 상태 초기화
if "results" not in st.session_state:
    st.session_state.results = []

# 사례 선택
record_titles = [f"{record['id']}. {record['title']}" for record in records]
selected_title = st.selectbox("진료기록 사례 선택", record_titles)

selected_index = record_titles.index(selected_title)
record = records[selected_index]

st.subheader("1. 원본 SOAP 진료기록")
st.text_area(
    "원본 기록",
    value=record["original"],
    height=300
)

st.subheader("2. AI 요약문 비교")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 일반 요약")
    st.text_area(
        "일반 요약문",
        value=record["general_summary"],
        height=220
    )

with col2:
    st.markdown("### 구조화 요약")
    st.text_area(
        "구조화 요약문",
        value=record["structured_summary"],
        height=220
    )

st.divider()

st.subheader("3. 핵심정보 보존 여부 평가")
st.write("각 핵심정보가 요약문에 정확히 반영되었는지 확인하세요.")

evaluation_rows = []

for info in record["key_info"]:
    st.markdown(f"**핵심정보: {info}**")

    col1, col2 = st.columns(2)

    with col1:
        general_check = st.checkbox(
            "일반 요약에 포함됨",
            key=f"general_{record['id']}_{info}"
        )

    with col2:
        structured_check = st.checkbox(
            "구조화 요약에 포함됨",
            key=f"structured_{record['id']}_{info}"
        )

    evaluation_rows.append({
        "사례": record["title"],
        "핵심정보": info,
        "일반 요약 보존": general_check,
        "구조화 요약 보존": structured_check
    })

st.divider()

st.subheader("4. 오류 유형 기록")

error_options = ["없음", "누락", "왜곡", "수치 오류", "허위정보 추가", "불명확 표현"]

general_error = st.multiselect(
    "일반 요약에서 발견된 오류 유형",
    error_options,
    default=["없음"],
    key=f"general_error_{record['id']}"
)

structured_error = st.multiselect(
    "구조화 요약에서 발견된 오류 유형",
    error_options,
    default=["없음"],
    key=f"structured_error_{record['id']}"
)

st.subheader("5. 최종 수정 요약문")
final_summary = st.text_area(
    "검토 후 수정한 최종 요약문을 입력하세요.",
    height=180,
    placeholder="AI 요약문을 바탕으로 누락된 핵심정보를 보완하여 최종 요약문을 작성하세요."
)

if st.button("평가 결과 저장"):
    general_preserved = sum(row["일반 요약 보존"] for row in evaluation_rows)
    structured_preserved = sum(row["구조화 요약 보존"] for row in evaluation_rows)
    total_info = len(evaluation_rows)

    result = {
        "사례": record["title"],
        "전체 핵심정보 수": total_info,
        "일반 요약 보존 수": general_preserved,
        "구조화 요약 보존 수": structured_preserved,
        "일반 요약 정확도": round(general_preserved / total_info * 100, 1),
        "구조화 요약 정확도": round(structured_preserved / total_info * 100, 1),
        "일반 요약 오류": ", ".join(general_error),
        "구조화 요약 오류": ", ".join(structured_error),
        "최종 수정 요약문": final_summary
    }

    st.session_state.results.append(result)
    st.success("평가 결과가 저장되었습니다.")

st.divider()

st.subheader("6. 평가 결과 표")

if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df, use_container_width=True)

    st.subheader("7. 요약 방식별 정확도 그래프")

    avg_general = df["일반 요약 정확도"].mean()
    avg_structured = df["구조화 요약 정확도"].mean()

    chart_df = pd.DataFrame({
        "요약 방식": ["일반 요약", "구조화 요약"],
        "평균 정확도": [avg_general, avg_structured]
    })

    st.bar_chart(
        chart_df,
        x="요약 방식",
        y="평균 정확도"
    )

    st.write(f"일반 요약 평균 정확도: **{avg_general:.1f}%**")
    st.write(f"구조화 요약 평균 정확도: **{avg_structured:.1f}%**")

else:
    st.info("아직 저장된 평가 결과가 없습니다.")
