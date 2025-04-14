import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Phân tích Tài/Xỉu", layout="centered")

st.title("🎲 Phân tích và Dự đoán Tài/Xỉu theo tổng điểm")

# Nhập dữ liệu tổng điểm
st.subheader("⬇️ Nhập danh sách tổng điểm các phiên")
total_input = st.text_area("Nhập cách nhau bởi dấu phẩy (,)", "12,9,4,11,10,14,8,13,9,15,10,12,11")

try:
    totals = [int(x.strip()) for x in total_input.split(",") if x.strip().isdigit()]
except:
    st.error("Dữ liệu không hợp lệ. Hãy chắc chắn rằng bạn nhập toàn số, phân cách bằng dấu phẩy.")
    st.stop()

# Phân loại kết quả
def classify_result(total):
    if total in [3, 18]:
        return "Bộ ba"
    elif 4 <= total <= 10:
        return "Xỉu"
    elif 11 <= total <= 17:
        return "Tài"
    else:
        return "Lỗi"

# Phân tích kết quả
def analyze_results(totals):
    stats = {"Tài": 0, "Xỉu": 0, "Bộ ba": 0, "Lỗi": 0}
    max_streak = {"Tài": 0, "Xỉu": 0, "Bộ ba": 0}

    results = []
    last = None
    current_streak = 0

    for total in totals:
        result = classify_result(total)
        results.append(result)
        stats[result] += 1

        if result == last:
            current_streak += 1
        else:
            current_streak = 1
            last = result

        if result in max_streak:
            max_streak[result] = max(max_streak[result], current_streak)

    return stats, max_streak, results

# Dự đoán xu hướng tiếp theo
def predict_next(results):
    if not results:
        return "Không đủ dữ liệu để dự đoán."

    last = results[-1]
    recent = results[-5:]

    if recent.count(last) >= 4:
        if last == "Xỉu":
            return "⏭ Dự đoán: Có thể chuyển sang **Tài**"
        elif last == "Tài":
            return "⏭ Dự đoán: Có thể chuyển sang **Xỉu**"
        else:
            return "⏭ Dự đoán: Bộ ba vừa ra – có thể quay lại Xỉu hoặc Tài"

    if len(set(recent)) >= 2 and recent[-2] != last:
        return f"⏭ Dự đoán: Có thể tiếp tục là **{last}**"

    return f"⏭ Dự đoán: Khả năng cao tiếp theo là **{last}**"

# Gợi ý kiểm soát vốn

def capital_control(totals, results):
    st.subheader("💰 Gợi ý kiểm soát vốn (10 tay gần nhất)")

    bet_unit = 10000
    max_bet = bet_unit * 4
    balance = 0
    bet = bet_unit
    prediction_base = results[-1] if results else ""

    results_sim = results[-10:] if len(results) >= 10 else results

    for i, actual in enumerate(results_sim):
        win = (actual == prediction_base)
        profit = bet if win else -bet
        balance += profit
        status = "✅ Thắng" if win else "❌ Thua"
        st.write(f"Tay {i+1}: cược {bet:,} → {status} → Lãi/Lỗ: {profit:+,}, Tổng: {balance:+,}")

        if win:
            bet = bet_unit
        else:
            bet = min(bet * 2, max_bet)

    if balance > 0:
        st.success(f"✅ Kế hoạch ổn. Sau 10 tay: Lợi nhuận {balance:,} VND")
    else:
        st.warning(f"⚠️ Cảnh báo. Sau 10 tay: Âm {balance:,} VND — cân nhắc lại chiến lược!")

# Hiển thị kết quả phân tích
stats, max_streak, results = analyze_results(totals)

st.subheader("📊 Kết quả từng phiên")
st.write(results)

st.subheader("🔢 Thống kê kết quả")
st.write(stats)

st.subheader("🔁 Chuỗi dài nhất")
st.write(max_streak)

st.subheader("🤖 Dự đoán xu hướng tiếp theo")
prediction = predict_next(results)
st.info(prediction)

capital_control(totals, results)

# Biểu đồ nhanh
st.subheader("📈 Biểu đồ Tài/Xỉu")
df_chart = pd.DataFrame(results, columns=["Kết quả"])
st.bar_chart(df_chart["Kết quả"].value_counts())
