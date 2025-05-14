# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------
# 頁面設定
# -------------------------------
st.set_page_config(page_title="資料與統計圖", layout="centered")
st.title("📊 柔道比賽資料與統計圖")
st.caption("本頁面展示 2020 與 2024 年度比賽的描述統計資訊，圖表標籤為英文。")
st.markdown("---")

# -------------------------------
# 載入資料
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

COLOR1 = "#92d4e0"
COLOR2 = "#e09294"
sns.set(style="whitegrid")

# -------------------------------
# 圖表 1
# -------------------------------
st.markdown("### 1. 每年比賽人次（依性別）")
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(data=df, x="year", hue="gender", palette=[COLOR1, COLOR2], ax=ax)
ax.set_title("Match Count per Year by Gender")
for container in ax.containers:
    ax.bar_label(container)
plt.tight_layout()
st.pyplot(fig)

# -------------------------------
# 圖表 2
# -------------------------------
st.markdown("### 2. 回合 × 類別 出賽數量")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, y="round", hue="category", order=df["round"].value_counts().index, palette=[COLOR1, COLOR2], ax=ax)
ax.set_title("Match Count by Round and Category")
plt.tight_layout()
st.pyplot(fig)

# -------------------------------
# 圖表 3
# -------------------------------
st.markdown("### 3. 每年 Ippon 出現次數")
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(data=df, x="year", hue="has_ippon", palette=[COLOR1, COLOR2], ax=ax)
ax.set_title("Ippon Count per Year")
ax.set_xlabel("Year")
ax.set_ylabel("Count")
ax.legend(title="Ippon", labels=["No", "Yes"])
for container in ax.containers:
    ax.bar_label(container)
plt.tight_layout()
st.pyplot(fig)

# -------------------------------
# 圖表 4
# -------------------------------
st.markdown("### 4. 總體 Ippon 機率")
fig, ax = plt.subplots(figsize=(5, 4))
sns.countplot(data=df, x="has_ippon", palette=[COLOR1], ax=ax)
ax.set_title("Ippon Occurrence")
ax.set_xticklabels(["No Ippon", "Ippon"])
for container in ax.containers:
    ax.bar_label(container)
plt.tight_layout()
st.pyplot(fig)

# -------------------------------
# 圖表 5
# -------------------------------
st.markdown("### 5. 比賽時間分布（秒）")
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(data=df, x="duration_sec", bins=30, kde=True, color=COLOR1, ax=ax)
ax.set_title("Match Duration (sec)")
plt.tight_layout()
st.pyplot(fig)

# -------------------------------
# 圖表 6
# -------------------------------
st.markdown("### 6. 雙方 Shido 數量")
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.countplot(data=df, x="winner_shido_count", color=COLOR1, ax=axes[0])
axes[0].set_title("Winner Shido Count")
sns.countplot(data=df, x="loser_shido_count", color=COLOR2, ax=axes[1])
axes[1].set_title("Loser Shido Count")
for ax in axes:
    for container in ax.containers:
        ax.bar_label(container)
plt.tight_layout()
st.pyplot(fig)

# -------------------------------
# 圖表 7
# -------------------------------
st.markdown("### 7. 勝者與敗者世界排名差距")
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(data=df, x="ranking_diff", bins=30, kde=True, color=COLOR1, ax=ax)
ax.axvline(x=0, color='red', linestyle='--')
ax.set_title("Winner - Loser Ranking Difference")
plt.tight_layout()
st.pyplot(fig)

# -------------------------------
# 圖表 8
# -------------------------------
st.markdown("### 8. Golden Score 發生次數")
fig, ax = plt.subplots(figsize=(5, 4))
sns.countplot(data=df, x="is_gs", palette=[COLOR1], ax=ax)
ax.set_title("Golden Score Occurrence")
ax.set_xticklabels(["False", "True"])
for container in ax.containers:
    ax.bar_label(container)
plt.tight_layout()
st.pyplot(fig)
