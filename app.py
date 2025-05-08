import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------
# 頁面設定
# -------------------------------
st.set_page_config(page_title="Judo Survival Predictor", layout="centered")
st.title("🥋 Judo Survival Predictor")
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
    "💪🏽 Match End after First Shido": "aft_end_first",
    "🏆 Ippon after Second Shido": "aft_ippon_second",
    "💪🏽 Match End after Second Shido": "aft_end_second"
}
selected_label = st.selectbox("Select AFT Model", list(model_options.keys()))
selected_model_key = model_options[selected_label]
aft_model = aft_models[selected_model_key]

# -------------------------------
# Gender 與 Weight Class：即時變更
# -------------------------------
st.subheader("📋 Select Match Conditions")

gender = st.selectbox("Gender", ["M", "F"])

# 根據 gender 顯示不同的量級
if gender == "M":
    weight_labels = [
        "Men -60 kg", "Men -66 kg", "Men -73 kg",
        "Men -81 kg", "Men -90 kg", "Men -100 kg", "Men +100 kg"
    ]
else:
    weight_labels = [
        "Women -48 kg", "Women -52 kg", "Women -57 kg",
        "Women -63 kg", "Women -70 kg", "Women -78 kg", "Women +78 kg"
    ]

weight_label = st.selectbox("Weight Class", weight_labels)
weight_rank = weight_labels.index(weight_label) + 1  # 編碼為 1~7

# -------------------------------
# 其餘條件輸入（包在 form 中）
# -------------------------------
with st.form(key="input_form"):
    col1, col2 = st.columns(2)
    with col1:
        winner_shido_count = st.selectbox("Winner's Shido Count", [0, 1, 2])
        year = st.selectbox("Match Year", [2020, 2024])
    with col2:
        winner_has_waza_ari = st.selectbox("Winner has Waza-ari", [0, 1])
        ranking_diff = st.slider("Ranking Difference (Winner - Rival)", -100, 100, 0)

    st.markdown("⏱ **Enter Time Point (in seconds)**")
    t_input = st.number_input("Time (0s ~ 800s)", min_value=0, max_value=800, value=60, step=1)

    submit = st.form_submit_button("Predict!")

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
    title = (
        f"Condition | "
        f"Weight: {weight_label}, "
        f"Shido: {winner_shido_count}, "
        f"Waza-ari: {'Yes' if winner_has_waza_ari == 1 else 'No'}, "
        f"Ranking Diff: {ranking_diff}, "
        f"Year: {year}"
    )
    ax.set_title(title, fontsize=12, pad=15)
    
    ax.plot(surv_func.index, surv_func.values[:, 0], label="S(t): Survival Probability", color="#92d4e0", linewidth=2.5)
    ax.plot(surv_func.index, 1 - surv_func.values[:, 0], label="1-S(t): End Probability", color="#e09294", linewidth=2.5)
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
    col1.metric("Survival Probability", f"{surv_prob * 100:.2f}%")
    col2.metric("End Probability", f"{(1 - surv_prob) * 100:.2f}%")
