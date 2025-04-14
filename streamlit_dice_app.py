import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Dự đoán xúc xắc", layout="centered")
st.title("🎲 Tool phân tích & dự đoán xúc xắc (3 con)")

# --- Nhập dữ liệu ---
st.header("📥 Nhập dữ liệu")

uploaded_file = st.file_uploader("Tải file dữ liệu (.txt hoặc .csv)", type=["txt", "csv"])
manual_input = st.text_area("Hoặc nhập thủ công (mỗi dòng: 3 số cách nhau bởi khoảng trắng):", height=200)

data = []

if uploaded_file:
    lines = uploaded_file.read().decode("utf-8").splitlines()
elif manual_input:
    lines = manual_input.strip().splitlines()
else:
    lines = []

for line in lines:
    try:
        values = list(map(int, line.strip().split()))
        if len(values) == 3 and all(1 <= v <= 6 for v in values):
            data.append(values)
    except:
        pass

if data:
    df = pd.DataFrame(data, columns=["Xúc xắc 1", "Xúc xắc 2", "Xúc xắc 3"])
    st.success(f"✅ Đã tải {len(df)} dòng dữ liệu")

    # Giới hạn 100 dòng gần nhất để phân tích xu hướng
    recent_df = df.tail(100)

    st.subheader("📋 100 lần gần nhất dùng để phân tích")
    st.dataframe(recent_df)

    st.header("📊 Phân tích & Gợi ý")

    for i in range(3):
        col_name = f"Xúc xắc {i+1}"
        counts = recent_df[col_name].value_counts().sort_index()
        st.subheader(f"🎲 {col_name} (trên 100 lần gần nhất)")
        st.bar_chart(counts)

        recent = recent_df[col_name].tail(10)
        most_common = recent.value_counts().idxmax()
        st.markdown(f"**🔍 Xu hướng gần đây (10 lần): `{most_common}`**")
        st.markdown(f"**🧠 Gợi ý giá trị tiếp theo: `{most_common}`**")

    # --- Đánh giá độ chính xác ---
    st.subheader("📈 Đánh giá độ chính xác (so sánh dự đoán với thực tế)")

    correct_count = 0
    total_predicts = 0

    for i in range(3):
        col_name = f"Xúc xắc {i+1}"
        col_values = recent_df[col_name]

        if len(col_values) < 11:
            st.info(f"Không đủ dữ liệu để đánh giá cho {col_name}")
            continue

        # Dự đoán từng bước từ dòng 10 trở đi
        for j in range(10, len(col_values)):
            recent_10 = col_values[j-10:j]
            predicted = recent_10.value_counts().idxmax()
            actual = col_values[j]
            if predicted == actual:
                correct_count += 1
            total_predicts += 1

    accuracy = correct_count / total_predicts if total_predicts > 0 else 0
    st.metric("🎯 Độ chính xác dự đoán", f"{accuracy*100:.2f}%")
else:
    st.warning("⚠️ Vui lòng nhập dữ liệu để phân tích.")
