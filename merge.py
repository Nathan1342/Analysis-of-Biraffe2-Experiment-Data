import pandas as pd

# --- load datasets ---
biosig = pd.read_csv("ALL_SUBJECTS_FEATURES.csv")   # ECG + EDA features
person = pd.read_csv("BIRAFFE2-metadata.csv", sep=";")  # demographics + traits

# --- ensure ID is consistent type ---
biosig["ID"] = biosig["ID"].astype(int)
person["ID"] = person["ID"].astype(int)

# --- optional: drop columns you don't need (adjust if needed) ---
cols_to_keep = [
    "ID", "AGE", "SEX",
    "OPENNESS", "CONSCIENTIOUSNESS",
    "NEUROTICISM", "AGREEABLENESS", "EXTRAVERSION"
]
person = person[cols_to_keep]

# --- merge ---
merged = biosig.merge(person, on="ID", how="left")

# --- save ---
merged.to_csv("merged_dataset.csv", index=False)

print(merged.head())