import pandas as pd

df_advanced = pd.read_csv("data/players/advanced.csv")

print(
    df_advanced[df_advanced["WS"] > 5.0][["Player", "Team", "WS", "WS/48"]]
    .sort_values(by="WS", ascending=False)
    .head(10)
)
