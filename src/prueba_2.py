from nba_api.stats.endpoints import teamgamelogs, scheduleleaguev2
import pandas as pd

sched = scheduleleaguev2.ScheduleLeagueV2(
    season="2026-27", timeout=30
).get_data_frames()[0]
# print(sched.columns.tolist())   # mira los nombres exactos de las columnas

df = sched[
    [
        "gameId",
        "gameDate",
        "homeTeam_teamName",
        "awayTeam_teamName",
        "homeTeam_score",
        "awayTeam_score",
    ]
]

df["gameDate"] = pd.to_datetime(
    df["gameDate"], format="%m/%d/%Y %H:%M:%S"
).dt.normalize()

df = df[(df["homeTeam_score"] > 0) & (df["awayTeam_score"] > 0)].sort_values(
    by="gameDate", ascending=True
)

df = df[df["gameDate"] >= "10-20-2026"]

df.to_csv("data/results_2627.csv", index=False)
