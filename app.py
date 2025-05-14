import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------
# 頁面設定
# -------------------------------
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

# 模型選擇（中文顯示）
model_options = {
    "🏆 對手第一次Shido後，我方Ippon": "aft_ippon_first",
    "💪🏽 對手第一次Shido後，我方獲勝": "aft_end_first",
    "🏆 對手第二次Shido後，我方Ippon": "aft_ippon_second",
    "💪🏽 對手第二次Shido後，我方獲勝": "aft_end_second"
}
selected_label = st.selectbox("💡 請選擇預測場景", list(model_options.keys()))
selected_model_key = model_options[selected_label]
aft_model = aft_models[selected_model_key]

# -------------------------------
# 比賽設定輸入
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
weight_rank = weight_labels.index(weight_label) + 1

# 圖表用英文對照
weight_map_en = {
    "男子 -60 kg": "Men -60 kg",     "男子 -66 kg": "Men -66 kg",     "男子 -73 kg": "Men -73 kg",
    "男子 -81 kg": "Men -81 kg",     "男子 -90 kg": "Men -90 kg",     "男子 -100 kg": "Men -100 kg",
    "男子 +100 kg": "Men +100 kg",   "女子 -48 kg": "Women -48 kg",   "女子 -52 kg": "Women -52 kg",
    "女子 -57 kg": "Women -57 kg",   "女子 -63 kg": "Women -63 kg",   "女子 -70 kg": "Women -70 kg",
    "女子 -78 kg": "Women -78 kg",   "女子 +78 kg": "Women +78 kg"
}
weight_label_en = weight_map_en.get(weight_label, weight_label)

# -------------------------------
# 其他條件輸入
# -------------------------------
with st.form(key="input_form"):
    col1, col2 = st.columns(2)
    with col1:
        winner_shido_count = st.selectbox("📛 我方得到幾次Shido？", [0, 1, 2])
        year = st.selectbox("📅 比賽年份", [2020, 2024])
    with col2:
        winner_has_waza_ari = st.selectbox("⚡ 我方有Waza-ari嗎？", [0, 1])
        ranking_diff = st.slider("📊 世界排名差距（勝者 - 敗者）", -100, 100, 0)

    is_gs = st.selectbox("🕒 這場有打到黃金得分嗎？", ["否", "是"]) == "是"

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

    # 🎯 擷取獲勝機率 (1 - S)
    win_prob = 1 - surv_func.values[:, 0]
    selected_win_prob = np.interp(t_input, surv_func.index, win_prob)

    st.subheader("📈 指定條件下的獲勝機率")

    fig, ax = plt.subplots()

    # 🎯 主曲線：1 - S(t)
    ax.plot(surv_func.index, win_prob, label="Win Probability", color="#e09294", linewidth=2.5)
    
    # 🎯 垂直虛線：從 x 軸畫到交會點 y
    ax.vlines(x=t_input, ymin=0, ymax=selected_win_prob, color='gray', linestyle='--')
    
    # 🎯 水平虛線：從 y 軸畫到交會點 x
    ax.hlines(y=selected_win_prob, xmin=0, xmax=t_input, color='gray', linestyle='--')
    
    # 🎯 交會點圓點
    ax.scatter(t_input, selected_win_prob, color="white", edgecolor="black", zorder=5)
    
    # 🎯 標註文字
    ax.text(t_input + 10, selected_win_prob, f"{selected_win_prob*100:.1f}%", color="#e09294", va='center')
    
    # 🔧 標籤與樣式
    ax.set_xlabel("Match Time (sec)")
    ax.set_ylabel("Win Probability")
    ax.set_xlim([0, 800])
    ax.set_ylim([0, 1])
    ax.grid(alpha=0.3)
    
    st.pyplot(fig)


    # 🎯 預測結果數值顯示
    st.markdown(f"### 🧮 在 {t_input} 秒的預測結果")
    st.metric("☠️ 獲勝機率", f"{selected_win_prob * 100:.2f}%")

