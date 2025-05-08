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
st.caption("Explore winning probabilities under different match conditions.")

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
    "🏁 Match End after First Shido": "aft_end_first",
    "🥋 Ippon after Second Shido": "aft_ippon_second",
    "⏱ Match End after Second Shido": "aft_end_second"
}
selected_label = st.selectbox("Select AFT Model", list(model_options.keys()))
selected_model_key = model_options[selected_label]
aft_model = aft_models[selected_model_key]

# -------------------------------
# 條件輸入表單區塊
# -------------------------------
with st.form(key="input_form"):
    st.subheader("📋 Select Match Conditions")

    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Gender", ["M", "F"])
        winner_shido_count = st.selectbox("Winner's Shido Count", [0, 1, 2])
        weight_rank = st.selectbox("Weight Rank (custom encoded)", [1, 2, 3, 4, 5])
    with col2:
        winner_has_waza_ari = st.selectbox("Winner has Waza-ari", [0, 1])
        year = st.selectbox("Match Year", [2020, 2024])
        ranking_diff = st.slider("Ranking Difference (Winner - Rival)", -30, 30, 0)

    st.markdown("⏱ **Enter Time Point (in seconds)**")
    t_input = st.number_input("Time", min_value=0, max_value=800, value=60, step=1)

    submit = st.form_submit_button("🔁 Update Prediction")

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
        "year": year
    }])

    timeline = np.linspace(0, 800, 500)
    surv_func = aft_model.predict_survival_function(X, times=timeline)

    st.subheader("📈 Survival Probability Curve")

    fig, ax = plt.subplots()
    ax.plot(surv_func.index, surv_func.values[:, 0], label="🟦 S(t) Survival", color="#1f77b4", linewidth=2.5)
    ax.plot(surv_func.index, 1 - surv_func.values[:, 0], label="🟥 1 - S(t) End", color="#d62728", linewidth=2.5)
    ax.axvline(x=t_input, color='gray', linestyle='--')
    ax.set_xlabel("Time (sec)")
    ax.set_ylabel("Probability")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    # 顯示數值
    st.markdown("### 📊 Predicted Probabilities at Selected Time")
    surv_prob = np.interp(t_input, surv_func.index, surv_func.values[:, 0])
    col1, col2 = st.columns(2)
    col1.metric("S(t) – Survival", f"{surv_prob * 100:.2f}%")
    col2.metric("1 - S(t) – End", f"{(1 - surv_prob) * 100:.2f}%")
