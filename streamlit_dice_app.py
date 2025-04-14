import streamlit as st
import pandas as pd

st.set_page_config(page_title="Phân tích Tài/Xỉu", layout="centered")
st.title("🎲 Tool phân tích & dự đoán Tài/Xỉu (3 xúc xắc)")

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
    df["Tổng"] = df.sum(axis=1)
    df["Tài/Xỉu"] = df["Tổng"].apply(lambda x: "Xỉu" if x <= 10 else "Tài")

    recent_df = df.tail(100)
    st.success(f"✅ Đã nạp {len(df)} dòng dữ liệu — phân tích 100 dòng gần nhất")

    st.subheader("📋 Dữ liệu 100 lần gần nhất")
    st.dataframe(recent_df)

    st.header("📊 Phân tích Tài/Xỉu")

    counts = recent_df["Tài/Xỉu"].value_counts()
    st.bar_chart(counts)

    # --- Dự đoán kết quả tiếp theo ---
    st.header("🔮 Dự đoán lần tiếp theo")

    full_tai_xiu = list(df["Tài/Xỉu"])
    last_1000 = full_tai_xiu[-1000:] if len(full_tai_xiu) >= 1000 else full_tai_xiu
    predicted_next = pd.Series(last_1000).value_counts().idxmax()

    st.markdown(f"**📌 Dự đoán Tài/Xỉu lần kế tiếp (dựa vào {len(last_1000)} lần gần nhất): `{predicted_next}`**")

    # --- Đánh giá độ chính xác ---
    st.header("📈 Đánh giá độ chính xác dự đoán")

    recent_tai_xiu = list(recent_df["Tài/Xỉu"])
    correct = 0
    total = 0
    for i in range(10, len(recent_tai_xiu)):
        prev_10 = recent_tai_xiu[i-10:i]
        pred = pd.Series(prev_10).value_counts().idxmax()
        actual = recent_tai_xiu[i]
        if pred == actual:
            correct += 1
        total += 1

    acc = correct / total if total else 0
    st.metric("🎯 Độ chính xác dự đoán (10 gần nhất)", f"{acc*100:.2f}%")

    # --- Gợi ý kiểm soát vốn ---
    st.header("💰 Gợi ý kiểm soát vốn cho 10 tay")

    base_bet = st.number_input("🔢 Nhập mức cược cơ bản (VD: 10000)", min_value=1000, value=10000, step=1000)

    sim_tai_xiu = recent_tai_xiu[-10:] if len(recent_tai_xiu) >= 10 else recent_tai_xiu
    sim_results = []
    balance = 0
    bet = base_bet

    for i in range(10):
        actual = sim_tai_xiu[i % len(sim_tai_xiu)]  # Lặp lại nếu không đủ 10 kết quả
        win = (actual == predicted_next)
        profit = bet if win else -bet
        balance += profit
        sim_results.append({
            "Tay": i+1,
            "Cược": bet,
            "Thắng": "✅" if win else "❌",
            "Lãi/lỗ": profit,
            "Tổng cộng": balance
        })
        bet = base_bet if win else min(bet * 2, base_bet * 4)

    sim_df = pd.DataFrame(sim_results)
    st.dataframe(sim_df)

    if balance >= 0:
        st.success(f"✅ Kế hoạch OK. Sau 10 tay bạn **lãi {balance:,.0f} VND**.")
    else:
        st.error(f"⚠️ Sau 10 tay bạn **lỗ {balance:,.0f} VND**. Cân nhắc điều chỉnh chiến lược.")
else:
    st.warning("⚠️ Vui lòng nhập dữ liệu hợp lệ (3 số từ 1-6 trên mỗi dòng).")
