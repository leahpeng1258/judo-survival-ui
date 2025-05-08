import streamlit as st
import pickle
import numpy as np
import matplotlib
import matplotlib.pyplot as plt  # 這是畫圖用
import pandas as pd

# 設定中文字型（建議 Noto Sans TC，需系統有安裝）
matplotlib.rcParams['font.family'] = 'Noto Sans TC'
matplotlib.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="柔道求生預測器", layout="centered")
st.title("🥋 柔道求生預測器")
st.caption("來看看在各種條件下你撐得過幾秒！")

st.markdown("---")

# -------------------------------
# 載入模型
# -------------------------------
@st.cache_resource
def load_models():
    with open("judo_aft_models.pkl", "rb") as f:
        return pickle.load(f)

aft_models = load_models()

# 模型選擇
model_options = {
    "🏆 Ippon after First Shido": "aft_ippon_first",
    "💪🏽 Match End after First Shido": "aft_end_first",
    "🏆 Ippon after Second Shido": "aft_ippon_second",
    "💪🏽 Match End after Second Shido": "aft_end_second"
}
selected_label = st.selectbox("💡 請選擇預測場景", list(model_options.keys()))
selected_model_key = model_options[selected_label]
aft_model = aft_models[selected_model_key]

# -------------------------------
# Gender 與 Weight Class：即時變更
# -------------------------------
st.subheader("📋 請輸入比賽設定")

gender = st.selectbox("👥 比賽性別", ["M", "F"])

if gender == "M":
    weight_labels = [
        "男子 -60 kg", "男子 -66 kg", "男子 -73 kg",
        "男子 -81 kg", "男子 -90 kg", "男子 -100 kg", "男子 +100 kg"
    ]
else:
    weight_labels = [
        "女子 -48 kg", "女子 -52 kg", "女子 -57 kg",
        "女子 -63 kg", "女子 -70 kg", "女子 -78 kg", "女子 +78 kg"
    ]

weight_label = st.selectbox("🏋️‍♂️ 重量級別", weight_labels)
weight_rank = weight_labels.index(weight_label) + 1  # 編碼為 1~7

# -------------------------------
# 其餘條件輸入（包在 form 中）
# -------------------------------
with st.form(key="input_form"):
    col1, col2 = st.columns(2)
    with col1:
        winner_shido_count = st.selectbox("📛 得勝方獲得幾次指導？", [0, 1, 2])
        year = st.selectbox("📅 比賽年份", [2020, 2024])
    with col2:
        winner_has_waza_ari = st.selectbox("⚡ 得勝方有技有嗎？", [0, 1])
        ranking_diff = st.slider("📊 世界排名差距（勝者 - 敗者）", -100, 100, 0)

    is_gs = st.selectbox("🕒 這場打到延長賽了嗎？", ["否", "是"]) == "是"

    st.markdown("⏱ **預測某個時間點的機率**")
    t_input = st.number_input("請輸入秒數（0 到 800 秒）", min_value=0, max_value=800, value=60, step=1)

    submit = st.form_submit_button("🔮 開始預測！")

# -------------------------------
# 生存函數預測與繪圖
# -------------------------------
if submit:
    X = pd.DataFrame([{
        "gender": gender,
        "winner_shido_count": winner_shido_count,
        "winner_has_waza_ari": winner_has_waza_ari,
        "ranking_diff": ranking_diff,
        "weight_rank": weight_rank,
        "year": year,
        "is_gs": is_gs
    }])

    timeline = np.linspace(0, 800, 500)
    surv_func = aft_model.predict_survival_function(X, times=timeline)

    st.subheader("📈 撐住機率 VS 結束機率")

    fig, ax = plt.subplots()
    title = (
        f"條件｜"
        f"{weight_label}、"
        f"指導數: {winner_shido_count}、"
        f"技有: {'有' if winner_has_waza_ari == 1 else '無'}、"
        f"排名差: {ranking_diff}、"
        f"年份: {year}、"
        f"延長賽: {'是' if is_gs else '否'}"
    )
    ax.set_title(title, fontsize=12, pad=15)

    ax.plot(surv_func.index, surv_func.values[:, 0], label="撐住機率 💪", color="#92d4e0", linewidth=2.5)
    ax.plot(surv_func.index, 1 - surv_func.values[:, 0], label="結束機率 ☠️", color="#e09294", linewidth=2.5)
    ax.axvline(x=t_input, color='gray', linestyle='--')
    ax.set_xlabel("比賽進行時間（秒）")
    ax.set_ylabel("機率")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    st.markdown("### 🧮 在指定秒數的預測結果")
    surv_prob = np.interp(t_input, surv_func.index, surv_func.values[:, 0])
    col1, col2 = st.columns(2)
    col1.metric("撐住機率 💪", f"{surv_prob * 100:.2f}%")
    col2.metric("結束機率 ☠️", f"{(1 - surv_prob) * 100:.2f}%")
