import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# =========================================================
# LOAD + CLEAN
# =========================================================
df = pd.read_csv("merged_dataset.csv")
df_clean = df[df['quality_flag'] == 'OK'].copy()

# Remove extreme outlier: HR > mean + 3*SD
hr_mean = df_clean['mean_HR_bpm'].mean()
hr_std = df_clean['mean_HR_bpm'].std()
df_clean = df_clean[df_clean['mean_HR_bpm'] <= hr_mean + 3*hr_std]

df_clean["SEX"] = df_clean["SEX"].map({"M": "Male", "F": "Female"})

# =========================================================
# VARIABLES
# =========================================================
traits = [
    "OPENNESS",
    "CONSCIENTIOUSNESS",
    "NEUROTICISM",
    "AGREEABLENESS",
    "EXTRAVERSION"
]

physio = [
    "mean_HR_bpm",
    "SDNN_ms",
    "RMSSD_ms",
    "pNN50",
    "SCL_mean",
    "SCR_count"
]

# =========================================================
# 1. DATASET OVERVIEW
# =========================================================
plt.figure(figsize=(6,4))
sns.countplot(data=df_clean, x="SEX")
plt.title("Gender distribution")
plt.show()

plt.figure(figsize=(10,6))
df_clean[traits].hist(bins=10, figsize=(10,6))
plt.suptitle("Personality trait distributions")
plt.show()

# =========================================================
# 2. CORRELATION STRUCTURE (cleaner interpretation)
# =========================================================
plt.figure(figsize=(12, 8))
sns.heatmap(
    df_clean[physio + traits].corr().loc[physio, traits],
    cmap="coolwarm",
    center=0
)
plt.title("Physiology ↔ Personality (Core Relationships)")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# =========================================================
# 3. Visualising all relationships between traits and physiology
# =========================================================
for trait in traits:
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    sns.set_style("whitegrid")
    scatter_kws = {'alpha': 0.7, 's': 40}
    reg_kws = {'scatter_kws': scatter_kws, 'line_kws': {'color': 'red'}}

    # ------ 3a. Trait vs Mean HR ------
    sns.regplot(ax=axes[0], data=df_clean, x=trait, y='mean_HR_bpm', **reg_kws)
    axes[0].set_xlabel(trait)
    axes[0].set_ylabel('Mean HR (bpm)')
    axes[0].set_title(trait + ' vs Mean Heart Rate')
    r = df_clean[trait].corr(df_clean['mean_HR_bpm'])
    axes[0].text(0.05, 0.95, f'r = {r:.2f}', transform=axes[0].transAxes, fontsize=11,
                 verticalalignment='top')

    # ------ 3b. Trait vs SDNN_ms ------
    sns.regplot(ax=axes[1], data=df_clean, x=trait, y='SDNN_ms', **reg_kws)
    axes[1].set_xlabel(trait)
    axes[1].set_ylabel('SDNN_ms')
    axes[1].set_title(trait + ' vs SDNN_ms')
    r = df_clean[trait].corr(df_clean['SDNN_ms'])
    axes[1].text(0.05, 0.95, f'r = {r:.2f}', transform=axes[1].transAxes, fontsize=11,
                 verticalalignment='top')

    # ------ 3c. Trait vs RMSSD_ms ------
    sns.regplot(ax=axes[2], data=df_clean, x=trait, y='RMSSD_ms', **reg_kws)
    axes[2].set_xlabel(trait)
    axes[2].set_ylabel('RMSSD (ms)')
    axes[2].set_title(trait + ' vs RMSSD_ms')
    r = df_clean[trait].corr(df_clean['RMSSD_ms'])
    axes[2].text(0.05, 0.95, f'r = {r:.2f}', transform=axes[2].transAxes, fontsize=11,
                 verticalalignment='top')

    # ------ 3d. Neuroticism vs pNN50 ------
    sns.regplot(ax=axes[3], data=df_clean, x=trait, y='pNN50', **reg_kws)
    axes[3].set_xlabel(trait)
    axes[3].set_ylabel('pNN50')
    axes[3].set_title(trait + ' vs pNN50')
    r = df_clean[trait].corr(df_clean['pNN50'])
    axes[3].text(0.05, 0.95, f'r = {r:.2f}', transform=axes[3].transAxes, fontsize=11,
                 verticalalignment='top')

    # ------ 3e. Openness vs RMSSD (supplementary) ------
    sns.regplot(ax=axes[4], data=df_clean, x=trait, y='SCL_mean', **reg_kws)
    axes[4].set_xlabel(trait)
    axes[4].set_ylabel('SCL_mean')
    axes[4].set_title(trait + ' vs SCL_mean')
    r = df_clean[trait].corr(df_clean['SCL_mean'])
    axes[4].text(0.05, 0.95, f'r = {r:.2f}', transform=axes[4].transAxes, fontsize=11,
                 verticalalignment='top')

    # ------ 3e. Openness vs RMSSD (supplementary) ------
    sns.regplot(ax=axes[5], data=df_clean, x=trait, y='SCR_count', **reg_kws)
    axes[5].set_xlabel(trait)
    axes[5].set_ylabel('SCR_count')
    axes[5].set_title(trait + ' vs SCR_count')
    r = df_clean[trait].corr(df_clean['SCR_count'])
    axes[5].text(0.05, 0.95, f'r = {r:.2f}', transform=axes[5].transAxes, fontsize=11,
                 verticalalignment='top')

    plt.tight_layout()
    plt.show()

# =========================================================
# 5. SEX DIFFERENCES (IMPROVED: box + points)
# =========================================================

# RMSSD
plt.figure(figsize=(8,5))
sns.boxplot(data=df, x="SEX", y="RMSSD_ms", showfliers=False)
sns.stripplot(data=df, x="SEX", y="RMSSD_ms",
              color="black", alpha=0.4, jitter=0.25)

plt.title("RMSSD differences by sex")
plt.show()

# SCL
plt.figure(figsize=(8,5))
sns.boxplot(data=df, x="SEX", y="SCL_mean", showfliers=False)
sns.stripplot(data=df, x="SEX", y="SCL_mean",
              color="black", alpha=0.4, jitter=0.25)

plt.title("SCL differences by sex")
plt.show()

