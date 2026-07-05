import pandas as pd

# Lecture des datasets
crop = pd.read_csv("data/raw/Crop_recommendation.csv")
yield_df = pd.read_csv("data/raw/yield.csv")

print("=" * 50)
print("Crop Recommendation Dataset")
print("=" * 50)
print(crop.info())
print(crop.head())
print(crop.describe())
print(crop.isnull().sum())
print("Doublons :", crop.duplicated().sum())

print("\n" + "=" * 50)
print("Yield Dataset")
print("=" * 50)
print(yield_df.info())
print(yield_df.head())
print(yield_df.describe(include="all"))
print(yield_df.isnull().sum())
print("Doublons :", yield_df.duplicated().sum())