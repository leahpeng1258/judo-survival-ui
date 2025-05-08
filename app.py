import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------
# 頁面設定
# -------------------------------
st.set_page_config(page_title="Judo Survival Predictor", layout="centered")

st.title("🥋 Judo Survival Probability Explorer")
st.caption("Explore winning probabilities based on match conditions using a Log-Normal AFT survival model.")

st.markdown("---")

# -------------------------------
# 載入模型
# -------------------------------
@st.cache_resource
def load_models():
    with open("judo_aft_models.pkl", "rb") as f:
        return pickle.load(f)

aft_models = load_models()

# 模型選單
model_options = {
    "🏆 Ippon after First Shido": "aft_ippon_first",
    "🏁 Match End after First Shido": "aft_end_first",
    "🥋 Ippon after Second Shido": "aft_ippon_second",
    "⏱ Match End after Second Shido": "aft_end_second"
}
selected_label = st.selectbox("Select Model Type", list(model_options.keys()))
selected_model_key = model_options[selected_label]
aft_model = aft_models[selected_model_key]

st.markdown("---")

# -------------------------------
# Sidebar 輸入參數
# -------------------------------
st.sidebar.header("📌 Match Conditions")

gender = st.sidebar.radio("Gender", ["M", "F"])
winner_shido_count = st.sidebar.selectbox("Winner's Shido Count", [0, 1, 2])
winner_has_waza_ari = st.sidebar.selectbox("Winner has Waza-ari", [0, 1])
ranking_diff = st.sidebar.slider("Ranking Difference (Winner - Rival)", -30, 30, 0)
weight_rank = st.sidebar.selectbox("Weight Rank (custom encoded)", [1, 2, 3, 4, 5])
year = st.sidebar.selectbox("Year", [2020, 2024])

# -------------------------------
# 建立模型輸入資料
# -------------------------------
X = pd.DataFrame([{
    "gender": gender,
    "winner_shido_count": winner_shido_count,
    "winner_has_waza_ari": winner_has_waza_ari,
    "ranking_diff": ranking_diff,
    "weight_rank": weight_rank,
    "year": year
}])

# -------------------------------
# 使用者輸入時間點
# -------------------------------
st.subheader("⏱ Input Time (in seconds)")
t_input = st.number_input("Enter a time point", min_value=0, max_value=180, value=60, step=1)

# -------------------------------
# 生存函數預測 & 圖形輸出
# -------------------------------
timeline = np.linspace(0, 180, 200)
surv_func = aft_model.predict_survival_function(X, times=timeline)

st.subheader("📈 Survival Function Plot")

fig, ax = plt.subplots()
ax.plot(surv_func.index, surv_func.values[:, 0], label="S(t) – Survival")
ax.plot(surv_func.index, 1 - surv_func.values[:, 0], label="1 - S(t) – End Probability")
ax.axvline(x=t_input, color='gray', linestyle='--')
ax.set_xlabel("Time (sec)")
ax.set_ylabel("Probability")
ax.legend()
st.pyplot(fig)

# -------------------------------
# 顯示 S(t) / 1 - S(t)
# -------------------------------
st.markdown("### 📊 Predicted Probabilities at Selected Time")
surv_prob = np.interp(t_input, surv_func.index, surv_func.values[:, 0])

col1, col2 = st.columns(2)
col1.metric("Survival Probability S(t)", f"{surv_prob * 100:.2f}%")
col2.metric("End Probability 1 - S(t)", f"{(1 - surv_prob) * 100:.2f}%")
