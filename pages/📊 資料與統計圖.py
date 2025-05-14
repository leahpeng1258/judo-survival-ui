# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1️⃣ 每年比賽人次（依性別）
st.subheader("1️⃣ 每年比賽人次（依性別）")
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(data=df, x="year", hue="gender", palette=[COLOR1, COLOR2], ax=ax)
ax.set_title("Match Count per Year by Gender")  # 💬 英文標題
...

# 2️⃣ 回合 × 類別 出賽數量
st.subheader("2️⃣ 回合 × 類別 出賽數量")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, y="round", hue="category", order=df["round"].value_counts().index, palette=[COLOR1, COLOR2], ax=ax)
ax.set_title("Match Count by Round and Category")  # 💬 英文標題
...

# 3️⃣ 每年 Ippon 出現次數
st.subheader("3️⃣ 每年 Ippon 出現次數")
fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(data=df, x="year", hue="has_ippon", palette=[COLOR1, COLOR2], ax=ax)
ax.set_title("Ippon Count per Year")  # 💬 英文標題
...

# 4️⃣ 總體 Ippon 機率
st.subheader("4️⃣ 總體 Ippon 機率")
fig, ax = plt.subplots(figsize=(5, 4))
sns.countplot(data=df, x="has_ippon", palette=[COLOR1], ax=ax)
ax.set_title("Ippon Occurrence")  # 💬 保持英文
...

# 5️⃣ 比賽時間分布
st.subheader("5️⃣ 比賽時間分布（秒）")
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(data=df, x="duration_sec", bins=30, kde=True, color=COLOR1, ax=ax)
ax.set_title("Match Duration (sec)")  # 💬 保持英文
...

# 6️⃣ Shido 數量分布
st.subheader("6️⃣ 雙方 Shido 數量")
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.countplot(data=df, x="winner_shido_count", color=COLOR1, ax=axes[0])
axes[0].set_title("Winner Shido Count")  # 💬 保持英文
sns.countplot(data=df, x="loser_shido_count", color=COLOR2, ax=axes[1])
axes[1].set_title("Loser Shido Count")  # 💬 保持英文
...

# 7️⃣ 世界排名差距
st.subheader("7️⃣ 勝者與敗者世界排名差距")
fig, ax = plt.subplots(figsize=(6, 4))
sns.histplot(data=df, x="ranking_diff", bins=30, kde=True, color=COLOR1, ax=ax)
ax.axvline(x=0, color='red', linestyle='--')
ax.set_title("Winner - Loser Ranking Difference")  # 💬 保持英文
...

# 8️⃣ Golden Score 出現率
st.subheader("8️⃣ Golden Score 發生次數")
fig, ax = plt.subplots(figsize=(5, 4))
sns.countplot(data=df, x="is_gs", palette=[COLOR1], ax=ax)
ax.set_title("Golden Score Occurrence")  # 💬 保持英文
...
