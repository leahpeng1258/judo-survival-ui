import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 載入模型
@st.cache_resource
def load_models():
    with open("judo_aft_models.pkl", "rb") as f:
        return pickle.load(f)

aft_models = load_models()

# 選擇模型
model_options = {
    "🏆 Ippon after first Shido": "aft_ippon_first",
    "🏁 End after first Shido": "aft_end_first",
    "🥋 Ippon after second Shido": "aft_ippon_second",
    "⏱ End after second Shido": "aft_end_second"
}
selected_label = st.selectbox("Choose a model", list(model_options.keys()))
selected_model_key = model_options[selected_label]
aft_model = aft_models[selected_model_key]

# 輸入條件
st.sidebar.header("Input conditions")

gender = st.sidebar.selectbox("Gender", ["M", "F"])
round_ = st.sidebar.selectbox("Round", ["R16", "QF", "SF", "F"])
category = st.sidebar.selectbox("Category", ["-60", "-66", "-73", "-81", "Other"])
winner_shido_count = st.sidebar.selectbox("Winner Shido Count", [0, 1, 2])
winner_has_waza_ari = st.sidebar.selectbox("Winner has Waza-ari", [0, 1])
ranking_diff = st.sidebar.slider("Ranking Difference (Winner - Rival)", -30, 30, 0)

# 模擬輸入 DataFrame
X = pd.DataFrame([{
    "gender": gender,
    "round": round_,
    "category": category,
    "winner_shido_count": winner_shido_count,
    "winner_has_waza_ari": winner_has_waza_ari,
    "ranking_diff": ranking_diff
}])

# 輸入時間點
t_input = st.number_input("Enter a time point (seconds)", min_value=0, max_value=180, value=60)

# 生存函數預測
timeline = np.linspace(0, 180, 200)
surv_func = aft_model.predict_survival_function(X, times=timeline)

# 畫圖
st.subheader("Survival Probability vs. Time")
fig, ax = plt.subplots()
ax.plot(surv_func.index, surv_func.values[:, 0], label="S(t)")
ax.plot(surv_func.index, 1 - surv_func.values[:, 0], label="1 - S(t)")
ax.axvline(x=t_input, color='gray', linestyle='--')
ax.set_xlabel("Time (sec)")
ax.set_ylabel("Probability")
ax.legend()
st.pyplot(fig)

# 顯示指定時間點的機率
surv_prob = np.interp(t_input, surv_func.index, surv_func.values[:, 0])
st.metric("S(t)", f"{surv_prob * 100:.2f}%")
st.metric("1 - S(t)", f"{(1 - surv_prob) * 100:.2f}%")
# Streamlit app code will be added here.
