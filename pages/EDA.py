import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------
# 頁面標題與說明（繁體中文）
# -------------------------------
st.set_page_config(page_title="資料與統計圖", layout="centered")
st.title("📊 柔道比賽資料與統計圖")
st.caption("本頁面展示 2020 與 2024 年度比賽的描述統計資訊，圖表標籤為英文。")

st.markdown("---")
st.subheader("📥 載入資料")

# -------------------------------
# 載入 Google Sheet 原始資料
# -------------------------------
@st.cache_data
def load_data():
    url_2024 = "https://docs.google.com/spreadsheets/d/1c3vnGkJFP1ZnLTiW54Dc8cUiSA2tJySH/gviz/tq?tqx=out:csv&sheet=Sheet1"
    url_2020 = "https://docs.google.com/spreadsheets/d/1I0jK3VZYKENDvTVJUMZ-k66zQStT5Uo4/gviz/tq?tqx=out:csv&sheet=Sheet1"
    df_2024 = pd.read_csv(url_2024)
    df_2020 = pd.read_csv(url_2020)
    df_2024["year"] = 2024
    df_2020["year"] = 2020
    df = pd.concat([df_2024, df_2020], ignore_index=True)
    return df

df = load_data()
df["has_ippon"] = df["ippon_sec"].notnull()

# -------------------------------
# 統計圖表區塊
# -------------------------------

sns.set(style="whitegrid")

def plot_and_show(fig):
    st.pyplot(fig)

# 1️⃣ Year × Gender Count
st.subheader("1️⃣ Year × Gender Match Count")
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(data=df, x="year", hue="gender", ax=ax)
ax.set_title("Year × Gender Match Count")
for container in ax.containers:
    ax.bar_label(container)
st.pyplot(fig)

# 2️⃣ Round × Category
st.subheader("2️⃣ Round × Category Match Count")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, y="round", hue="category", order=df["round"].value_counts().index, ax=ax)
ax.set_title("Round × Category Match Count")
st.pyplot(fig)

# 3️⃣ Year × Ippon Count
st.subheader("3️⃣ Year × Ippon Count")
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(data=df, x="year", hue="has_ippon", ax=ax)
ax.set_title("Year × Ippon Count")
ax.set_xlabel("Year")
ax.set_ylabel("Count")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.legend(title="Ippon", labels=["No", "Yes"])
for container in ax.containers:
    ax.bar_label(container)
st.pyplot(fig)

# 4️⃣ Ippon Occurrence
st.subheader("4️⃣ Ippon Occurrence")
fig, ax = plt.subplots(figsize=(5, 4))
sns.countplot(data=df, x="has_ippon", ax=ax)
ax.set_title("Ippon Occurrence")
ax.set_xticklabels(["No Ippon", "Ippon"])
for container in ax.containers:
    ax.bar_label(container)
st.pyplot(fig)

# 5️⃣ Match Duration Histogram
st.subheader("5️⃣ Match Duration Distribution")
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(data=df, x="duration_sec", bins=30, kde=True, ax=ax)
ax.set_title("Match Duration (sec)")
st.pyplot(fig)

# 6️⃣ Shido Count
st.subheader("6️⃣ Shido Counts for Winner and Loser")
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.countplot(data=df, x="winner_shido_count", ax=axes[0])
axes[0].set_title("Winner Shido Count")
sns.countplot(data=df, x="loser_shido_count", ax=axes[1])
axes[1].set_title("Loser Shido Count")
for ax in axes:
    for container in ax.containers:
        ax.bar_label(container)
st.pyplot(fig)

# 7️⃣ Ranking Difference
st.subheader("7️⃣ Winner - Loser Ranking Difference")
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(data=df, x="ranking_diff", bins=30, kde=True, ax=ax)
ax.axvline(x=0, color='red', linestyle='--')
ax.set_title("Winner - Loser Ranking Difference")
st.pyplot(fig)

# 8️⃣ Golden Score
st.subheader("8️⃣ Golden Score Occurrence")
fig, ax = plt.subplots(figsize=(5, 4))
sns.countplot(data=df, x="is_gs", ax=ax)
ax.set_title("Golden Score Occurrence")
ax.set_xticklabels(["False", "True"])
for container in ax.containers:
    ax.bar_label(container)
st.pyplot(fig)
