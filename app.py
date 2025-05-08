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
    "🏆 對手第一次指導後，我方一本": "aft_ippon_first",
    "💪🏽 對手第一次指導後，比賽結束": "aft_end_first",
    "🏆 對手第二次指導後，我方一本": "aft_ippon_second",
    "💪🏽 對手第二次指導後，比賽結束": "aft_end_second"
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
        f"Condition | "
        f"Weight: {weight_label_en}, "
        f"Shido: {winner_shido_count}, "
        f"Waza-ari: {'Yes' if winner_has_waza_ari == 1 else 'No'}, "
        f"Ranking Diff: {ranking_diff}, "
        f"Year: {year}, "
        f"GS: {'Yes' if is_gs else 'No'}"
    )
    ax.set_title(title, fontsize=12, pad=15)

    ax.plot(surv_func.index, surv_func.values[:, 0], label="Survival Probability", color="#92d4e0", linewidth=2.5)
    ax.plot(surv_func.index, 1 - surv_func.values[:, 0], label="End Probability", color="#e09294", linewidth=2.5)
    ax.axvline(x=t_input, color='gray', linestyle='--')
    ax.set_xlabel("Match Time (sec)")
    ax.set_ylabel("Probability")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    st.markdown("### 🧮 在指定秒數的預測結果")
    surv_prob = np.interp(t_input, surv_func.index, surv_func.values[:, 0])
    col1, col2 = st.columns(2)
    col1.metric("撐住機率 💪", f"{surv_prob * 100:.2f}%")
    col2.metric("結束機率 ☠️", f"{(1 - surv_prob) * 100:.2f}%")

# -------------------------------
# 模型說明區塊
# -------------------------------
with st.expander("📘 模型說明與使用須知"):
    st.markdown("""
這個求生模型是根據過往柔道比賽資料所建立的時間預測模型，屬於 **Log-Normal AFT（加速失敗時間）模型**。

- **Survival Probability**（撐住機率）代表：選手在某個秒數還沒輸掉的機率。
- **End Probability**（結束機率）代表：比賽已經結束的累積機率。
- 模型會依照你的輸入條件（例如有沒有技有、獲得幾次指導、是否打到延長賽）來調整整體的生存曲線。
- 這些預測是根據統計趨勢，不是命運判定 😎

若你發現預測很離譜，請不要找裁判或我負責
    """)

with st.expander("🧬 使用變數一覽"):
    st.markdown("""
- 比賽性別（Gender）
- 重量級別（Weight Class）
- 得勝方獲得指導次數（Shido Count）
- 是否有技有（Waza-ari）
- 世界排名差距（Ranking Difference）
- 比賽年份（Year）
- 是否延長賽（Golden Score）
    """)
