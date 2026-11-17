import pandas as pd

df_25_26 = pd.read_csv("data/results/25-26/complete/results_2526.csv")
df_26_27 = pd.read_csv("data/results/26-27/complete/results_2627.csv")

df_count_25_26 = df_25_26[["Home/Neutral"]].groupby(by="Home/Neutral").value_counts()
df_count_26_27 = df_26_27[["Home/Neutral"]].groupby(by="Home/Neutral").value_counts()

print(df_count_25_26)
print(df_count_26_27)
